#include "sigfox_stack.h"
#include "S2LP_Middleware_Config.h"
#include "SDK_EVAL_Config.h"

#ifdef MONARCH_FEATURE_ENABLED
#include "st_monarch_api.h"
#endif

/* The RAMPS_IN_RAM symbol forces the ramps to be placed in RAM. It may be
useful if someone wants to use less flash occupation sacrifying some RAM */
//#define RAMPS_IN_RAM

/* The DEBUG symbol is used to print the names of the invoked functions */
//#define DEBUG

#ifdef DEBUG
void ST_dbg_CB(const char *vectcStr,...);
#define PRINTF(...)     { ST_dbg_CB(__VA_ARGS__);}
#elif DEBUG_BLE
#include "SDK_EVAL_Com.h"
#define PRINTF(...) printf(__VA_ARGS__)
#else
#define PRINTF(...)
#endif

static const uint8_t ST_RF_API_VER[ST_RF_API_VER_SIZE] = {'v','2','.','7','.','1'};

/* the array zeroes is used to implement waiting times in the TX FIFO */
static BUFF_PLACING uint8_t zeroes[]={0,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,\
  						   0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,\
                                        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};

uint8_t rampBuffer[82];
uint8_t bfSize;
static volatile uint8_t bSwap=0;
static volatile st_fifo_state_t _s2lpFIFOState;

static st_manuf_t st_manuf =
{
  .last_rssi_reg = 0,
  .priv_xtal_freq = XTAL_FREQUENCY,
  .lbt_thr_offset = 0,
  .smps_mode = 0,
  .tcxo_flag = 0,
  .pa_flag = 0,
  .tim_started = 0,
  .s2lp_irq_raised = 0,
  .api_timer_raised = 0,
  .api_timer_channel_clear_raised = 0,
  .manuf_state = ST_MANUF_STATE_IDLE,
  .rssi_offset = 0,
  .power_reduction = 0,
  .tx_is_ready = 0,
  .carrier_sense_tim_nested = 0
};

#define st_manuf_context        (&st_manuf)

/* SPI functions - these functions are implemented using the priv_ST_MANUF_SpiRaw */
static void priv_ST_MANUF_SpiRaw_Ramp(uint8_t n_bytes,uint8_t* buff_in, uint8_t* buff_out, uint8_t blocking)
{
  if(st_manuf_context->power_reduction!=0 && buff_in!=zeroes)
  {
    uint32_t i;
    uint8_t fifo_buff[82];
    fifo_buff[0]=buff_in[0];
    fifo_buff[1]=buff_in[1];
    for(i=2;i<n_bytes;i++)
    {
	if(((i%2)!=0) && (buff_in[i]+st_manuf_context->power_reduction<st_manuf_context->ramps_settings.min_power))
	  fifo_buff[i]=buff_in[i]+st_manuf_context->power_reduction;
	else
	  fifo_buff[i]=buff_in[i];
    }
    priv_ST_MANUF_SpiRaw_(n_bytes,fifo_buff,buff_out,blocking);
  }
  else
  {
    priv_ST_MANUF_SpiRaw_(n_bytes,buff_in,buff_out,blocking);
  }
}

/* command strobe - used to strobe commands to the S2-LP */
static void priv_ST_MANUF_CmdStrobe(uint8_t cmd)
{
  uint8_t tx_spi_buffer[2];

  tx_spi_buffer[0]=0x80;
  tx_spi_buffer[1]=cmd;

  priv_ST_MANUF_SpiRaw(2,tx_spi_buffer,NULL);
}

/* write registers function */
static void priv_ST_MANUF_WriteRegisters(uint8_t address, uint8_t n_bytes, uint8_t* buffer)
{
  uint8_t tx_spi_buffer[24];

  tx_spi_buffer[0]=0x00;
  tx_spi_buffer[1]=address;

  for(uint32_t i=0;i<n_bytes;i++)
  {
    tx_spi_buffer[i+2]=buffer[i];
  }

  priv_ST_MANUF_SpiRaw(n_bytes+2,tx_spi_buffer,NULL);
}

/* read registers function */
static void priv_ST_MANUF_ReadRegisters(uint8_t address, uint8_t n_bytes, uint8_t* buffer)
{
  uint8_t rx_spi_buffer[130],tx_spi_buffer[130];

  tx_spi_buffer[0]=0x01;
  tx_spi_buffer[1]=address;

  for(uint32_t i=0;i<n_bytes;i++)
  {
    tx_spi_buffer[i+2]=0xFF;
  }

  priv_ST_MANUF_SpiRaw(n_bytes+2,tx_spi_buffer,rx_spi_buffer);

  for(uint32_t i=0;i<n_bytes;i++)
  {
    buffer[i]=rx_spi_buffer[i+2];
  }
}

void priv_ST_MANUF_generateFIFORampsBuffer(st_ramp_buffer_t bufferType, uint8_t *pBuffer, uint8_t *pBufferSize, ramps_settings_t *rampsSettings)
{
  uint8_t j = 0;

  uint8_t auxBuff[] = {1, 1, 2, 2, 3, 4, 6, 8, 11, 14, 19, 23, 27, 31, 44, 220}; /* Default */
  uint8_t start_ramp[72] = {0};
  uint8_t start_ramp_tail[27] = {8,8,9,9,10,10,11,11,13,13,15,16,17,18,20,22,24,26,31,35,40,45,51,60,67,70,80};


  if(rampsSettings->gainFactor1 == 0x00)
  {
    auxBuff[9] =  15;
    auxBuff[10] = 20;
    auxBuff[11] = 24;
    auxBuff[12] = 30;
    auxBuff[13] = 39;
    auxBuff[14] = 54;
  }

  switch (bufferType)
  {
  case FIFO_RAMP_FAST:
    {
	*pBufferSize = 82;

	for(uint8_t i=0;i<15;i++)
	  auxBuff[i] += rampsSettings->gainFactor1;

	for(uint8_t i=2;i<17*2;i+=2)
	{
	  if (i<18){
	    pBuffer[i]=0;
	    pBuffer[i+1] = rampsSettings->max_power;
	  }

	  pBuffer[16+i]=0;
	  pBuffer[16+i+1]=auxBuff[j];

	  j+=1;
	}

	j=0;

	for(uint8_t i=0;i<16*2;i+=2)
	{
	  pBuffer[82-i-2]=0;
	  pBuffer[82-i-1]=auxBuff[j];
	  j+=1;
	}

	pBuffer[0] = 0x00;
	pBuffer[1] = 0xFF;

	break;
    }
  case FIFO_CONST_FAST:
    {
	*pBufferSize = 82;

	pBuffer[0] = 0x00;
	pBuffer[1] = 0xFF;

	for(uint8_t i=2;i<82;i+=2){
	    pBuffer[i]=0;
	    pBuffer[i+1] = rampsSettings->max_power;
	}

	break;
    }
  case FIFO_RAMP_DOWN_1:
    {
	*pBufferSize = 82;

	for(uint8_t i=0;i<46;i++)
	{
	  if(i < 10)
	    start_ramp[i] = 1;
	  if(i > 9 && i < 18)
	    start_ramp[i] = 2;
	  if(i > 17 && i < 25)
	    start_ramp[i] = 3;
	  if(i > 24 && i < 31)
	    start_ramp[i] = 4;
	  if(i > 30 && i < 36)
	    start_ramp[i] = 5;
	  if(i > 35 && i < 41)
	    start_ramp[i] = 6;
	  if(i > 40 && i < 45)
	    start_ramp[i] = 7;
	}

	memcpy(start_ramp + 45, start_ramp_tail, 27*sizeof(uint8_t));

	/* Scale start_ramp values */
	for(uint8_t i=0;i<72;i++)
	  start_ramp[i] += rampsSettings->gainFactor1;

	for(uint8_t i=2;i<18;i+=2){
	  pBuffer[i]=0;
	  pBuffer[i+1] = rampsSettings->max_power;
	}

	j=0;

	for(uint8_t i=0;i<(32*2);i+=2){
	  pBuffer[2*41-i-1]=start_ramp[32-j-1] + rampsSettings->gainFactor2;
	  pBuffer[2*41-i-2]=0;
	  j+=1;
	}

	pBuffer[0] = 0x00;
	pBuffer[1] = 0xFF;
	break;
    }
  case FIFO_RAMP_DOWN_2:
    {
	*pBufferSize = 82;

	for(uint8_t i=0;i<46;i++)
	{
	  if(i < 10)
	    start_ramp[i] = 1;
	  if(i > 9 && i < 18)
	    start_ramp[i] = 2;
	  if(i > 17 && i < 25)
	    start_ramp[i] = 3;
	  if(i > 24 && i < 31)
	    start_ramp[i] = 4;
	  if(i > 30 && i < 36)
	    start_ramp[i] = 5;
	  if(i > 35 && i < 41)
	    start_ramp[i] = 6;
	  if(i > 40 && i < 45)
	    start_ramp[i] = 7;
	}

	memcpy(start_ramp + 45, start_ramp_tail, 27*sizeof(uint8_t));

	/* Scale start_ramp values */
	for(uint8_t i=0;i<72;i++)
	  start_ramp[i] = start_ramp[i] + rampsSettings->gainFactor1;

	pBuffer[0] = 0x00;
	pBuffer[1] = 0xFF;

	j=0;

	for(uint8_t i=0;i<40*2;i+=2){
	  pBuffer[2*41-i-1]=start_ramp[72-j-1] + rampsSettings->gainFactor2;
	  pBuffer[2*41-i-2]=0;
	  j+=1;
	}

	break;
    }
  case FIFO_RAMP_UP_1:
    {
	*pBufferSize = 82;

	for(uint8_t i=0;i<46;i++)
	{
	  if(i < 10)
	    start_ramp[i] = 1;
	  if(i > 9 && i < 18)
	    start_ramp[i] = 2;
	  if(i > 17 && i < 25)
	    start_ramp[i] = 3;
	  if(i > 24 && i < 31)
	    start_ramp[i] = 4;
	  if(i > 30 && i < 36)
	    start_ramp[i] = 5;
	  if(i > 35 && i < 41)
	    start_ramp[i] = 6;
	  if(i > 40 && i < 45)
	    start_ramp[i] = 7;
	}

	memcpy(start_ramp + 45, start_ramp_tail, 27*sizeof(uint8_t));

	/* Scale start_ramp values */
	for(uint8_t i=0;i<72;i++)
	  start_ramp[i] = start_ramp[i] + rampsSettings->gainFactor1;

	j = 0;

	for(uint8_t i=2;i<81;i+=2)
	{
	  pBuffer[i]=0;
	  pBuffer[i+1]=start_ramp[72-j-1] + rampsSettings->gainFactor2;

	  j+=1;
	}

	pBuffer[0] = 0x00;
	pBuffer[1] = 0xFF;
	break;
    }
  case FIFO_RAMP_UP_2:
    {
	*pBufferSize = 66;

	for(uint8_t i=0;i<46;i++)
	{
	  if(i < 10)
	    start_ramp[i] = 1;
	  if(i > 9 && i < 18)
	    start_ramp[i] = 2;
	  if(i > 17 && i < 25)
	    start_ramp[i] = 3;
	  if(i > 24 && i < 31)
	    start_ramp[i] = 4;
	  if(i > 30 && i < 36)
	    start_ramp[i] = 5;
	  if(i > 35 && i < 41)
	    start_ramp[i] = 6;
	  if(i > 40 && i < 45)
	    start_ramp[i] = 7;
	}

	memcpy(start_ramp + 45, start_ramp_tail, 27*sizeof(uint8_t));

	/* Scale start_ramp values */
	for(uint8_t i=0;i<72;i++)
	  start_ramp[i] = start_ramp[i] + rampsSettings->gainFactor1;

	j = 40;

	for(uint8_t i=2;i<65;i+=2)
	{
	  pBuffer[i]=0;
	  pBuffer[i+1]=start_ramp[72-j-1] + rampsSettings->gainFactor2;

	  j+=1;
	}

	pBuffer[0] = 0x00;
	pBuffer[1] = 0xFF;
	break;
    }
  }
}

/* get XTAL frequency function */
static uint32_t privGetXtalFrequency(void)
{
  return st_manuf_context->priv_xtal_freq;
}

static void priv_ST_MANUF_tx_rf_init(void)
{
  uint8_t tmp;

  /* TX in direct via FIFO mode */
  tmp=0x04;
  priv_ST_MANUF_WriteRegisters(0x30, 1, &tmp);

  tmp=0x07;
  priv_ST_MANUF_WriteRegisters(0x62, 1, &tmp);

  /* disable NEWMODE */
  priv_ST_MANUF_ReadRegisters(0x63, 1, &tmp);
  tmp&=0xFD;
  priv_ST_MANUF_WriteRegisters(0x63, 1, &tmp);

  tmp=0xD7;
  priv_ST_MANUF_WriteRegisters(0x65, 1, &tmp);

  /* SMPS switch to 3MHz - ref. Datasheet page 23*/
  tmp=0x87;
  priv_ST_MANUF_WriteRegisters(0x76, 1, &tmp);

  tmp=0xFC;
  priv_ST_MANUF_WriteRegisters(0x77, 1, &tmp);

  tmp=0xC8;
  priv_ST_MANUF_WriteRegisters(0x64, 1, &tmp);

#ifdef MON_REF_DES
  if (st_manuf_context->pa_flag == 0)
    st_manuf_context->smps_mode=7;
#endif

  //Set the SMPS only for values from 1 to 7 (1.8V)
  if(st_manuf_context->smps_mode>0 && st_manuf_context->smps_mode<8)
  {
    /* (16dBm setting, SMPS to 1.8V -> smps_mode=7) */
    tmp=(st_manuf_context->smps_mode<<4)|0x02;
    priv_ST_MANUF_WriteRegisters(0x79, 1, &tmp);

    if(st_manuf_context->smps_mode>4)
    {
	tmp=0x88;
	priv_ST_MANUF_WriteRegisters(0x64, 1, &tmp);
    }
  }

  /* FIFO AE threshold to 48 bytes */
  tmp=48;
  priv_ST_MANUF_WriteRegisters(0x3F,1,&tmp);

  st_manuf_context->tx_is_ready=1;
}

static void priv_ST_MANUF_Get_Ramps_Settings(ramps_settings_t *rSettings)
{
  rSettings->gainFactor1 = 0x00;
  rSettings->gainFactor2 = 0x00;

  rSettings->fdev_pos = 0x7f;
  rSettings->fdev_neg = 0x81;
  rSettings->min_power = 220;

  rSettings->ramp_start_duration = 3;

  RangeExtType femType = S2LPManagementGetRangeExtender();

  switch(femType)
  {
  case RANGE_EXT_NONE:
    rSettings->ramp_start_duration = 18;
    rSettings->max_power = 1;
    break;
  case RANGE_EXT_SKYWORKS_SE2435L:
    rSettings->gainFactor1 = 0x22;
    rSettings->max_power = 35;
    break;
  case RANGE_EXT_SKYWORKS_SKY66420:
    if (st_manuf_context->pa_flag == 0)
    {
      rSettings->ramp_start_duration = 18;
      rSettings->max_power = 1;
    }
    else
    {
      rSettings->gainFactor1 = 0x04;
      rSettings->gainFactor2 = 0x02;
      rSettings->max_power = 5;
    }

    break;
  }
}

/* radio configuration for TX and RX */
static void priv_ST_MANUF_tx_rf_dbpsk_init(sfx_modulation_type_t type)
{
  uint32_t f_dig = privGetXtalFrequency();
  uint16_t dr_m;
  uint8_t mod_e,fdev_e,fdev_m;
  uint8_t regs[3];

  if(f_dig>DIG_DOMAIN_XTAL_THRESH) {
    f_dig >>= 1;
  }

  if(type==SFX_DBPSK_100BPS)
  {
    /* ETSI datarate is 100bps - chip datarate 500 (500*8/40=100) */

    /* modulation is POLAR | DR EXPONENT = 1 */
    mod_e=0x60|0x01;
    /* dr_num=(2**32)*500 */
    dr_m=(uint16_t)((uint64_t)0x1f400000000/f_dig-65536);

    /* understand if we are getting the nearest integer */
    uint64_t tgt1,tgt2;
    tgt1=(uint64_t)f_dig*((uint64_t)dr_m+65536);
    tgt2=(uint64_t)f_dig*((uint64_t)dr_m+1+65536);
    dr_m=((uint64_t)0x1f400000000-tgt1>tgt2-(uint64_t)0x1f400000000)?(dr_m+1):(dr_m);

    if(privGetXtalFrequency()>DIG_DOMAIN_XTAL_THRESH)
    {
    	fdev_e=0;
    	/* fdev_num=((2**22)*2000) */
    	fdev_m=(uint8_t)((uint64_t)8388608000/privGetXtalFrequency());
    	/* understand if we are getting the nearest integer */
    	uint64_t tgt1,tgt2;
    	tgt1=(uint64_t)privGetXtalFrequency()*((uint64_t)fdev_m);
    	tgt2=(uint64_t)privGetXtalFrequency()*((uint64_t)fdev_m+1);
    	fdev_m=((uint64_t)8388608000-tgt1>tgt2-(uint64_t)8388608000)?(fdev_m+1):(fdev_m);
    }
    else
    {
    	fdev_e=1;
    	fdev_m=(uint8_t)((uint64_t)8388608000/privGetXtalFrequency()-256);
    	/* understand if we are getting the nearest integer */
    	uint64_t tgt1,tgt2;
    	tgt1=(uint64_t)privGetXtalFrequency()*((uint64_t)fdev_m+256);
    	tgt2=(uint64_t)privGetXtalFrequency()*((uint64_t)fdev_m+1+256);
    	fdev_m=((uint64_t)8388608000-tgt1>tgt2-(uint64_t)8388608000)?(fdev_m+1):(fdev_m);
    }
  }
  else if(type==SFX_DBPSK_600BPS)
  {
    /* FCC datarate is 600bps - chip datarate 3000 (3000*8/40=600) */
    if (f_dig>24500000) //To consider also a margin used to compensate static drifts
    {
      /* modulation is POLAR | DR EXPONENT = 3 for xtal > 24 MHz */
      mod_e=0x60|0x03;
      /* dr_num=(2**30)*3000 */
      dr_m=(uint16_t)((uint64_t)0x2EE00000000/f_dig-65536);
      /* understand if we are getting the nearest integer */
      uint64_t tgt1,tgt2;
      tgt1=(uint64_t)f_dig*((uint64_t)dr_m+65536);
      tgt2=(uint64_t)f_dig*((uint64_t)dr_m+1+65536);
      dr_m=((uint64_t)0x2EE00000000-tgt1>tgt2-(uint64_t)0x2EE00000000)?(dr_m+1):(dr_m);
    }
    else
    {
      /* modulation is POLAR | DR EXPONENT = 4 for xtal=24 MHz */
      mod_e=0x60|0x04;
      /* dr_num=(2**30)*3000 */
      dr_m=(uint16_t)((uint64_t)0x17700000000/f_dig-65536);
      /* understand if we are getting the nearest integer */
      uint64_t tgt1,tgt2;
      tgt1=(uint64_t)f_dig*((uint64_t)dr_m+65536);
      tgt2=(uint64_t)f_dig*((uint64_t)dr_m+1+65536);
      dr_m=((uint64_t)0x17700000000-tgt1>tgt2-(uint64_t)0x17700000000)?(dr_m+1):(dr_m);
    }

    if(privGetXtalFrequency()>DIG_DOMAIN_XTAL_THRESH)
    {
	if(privGetXtalFrequency()<48500000) //To consider also a margin used to compensate static drifts
	{
	  fdev_e=3;
	  fdev_m=(uint8_t)((uint64_t)12582912000/privGetXtalFrequency()-256);
	  /* understand if we are getting the nearest integer */
	  uint64_t tgt1,tgt2;
	  tgt1=(uint64_t)privGetXtalFrequency()*((uint64_t)fdev_m+256);
	  tgt2=(uint64_t)privGetXtalFrequency()*((uint64_t)fdev_m+1+256);
	  fdev_m=((uint64_t)12582912000-tgt1>tgt2-(uint64_t)12582912000)?(fdev_m+1):(fdev_m);
	}
	else
	{
	  fdev_e=2;
	  fdev_m=(uint8_t)((uint64_t)25165824000/privGetXtalFrequency()-256);
	  /* understand if we are getting the nearest integer */
	  uint64_t tgt1,tgt2;
	  tgt1=(uint64_t)privGetXtalFrequency()*((uint64_t)fdev_m+256);
	  tgt2=(uint64_t)privGetXtalFrequency()*((uint64_t)fdev_m+1+256);
	  fdev_m=((uint64_t)25165824000-tgt1>tgt2-(uint64_t)25165824000)?(fdev_m+1):(fdev_m);
	}
    }
    else
    {
      if (f_dig>24500000) //To consider also a margin used to compensate static drifts
      {
      	fdev_e=3;
      	fdev_m=(uint8_t)((uint64_t)12582912000/privGetXtalFrequency()-256);
      	/* understand if we are getting the nearest integer */
      	uint64_t tgt1,tgt2;
      	tgt1=(uint64_t)privGetXtalFrequency()*((uint64_t)fdev_m+256);
      	tgt2=(uint64_t)privGetXtalFrequency()*((uint64_t)fdev_m+1+256);
      	fdev_m=((uint64_t)12582912000-tgt1>tgt2-(uint64_t)12582912000)?(fdev_m+1):(fdev_m);
      }
      else
      {
        fdev_e=4;
        fdev_m=(uint8_t)((uint64_t)6291456000/privGetXtalFrequency()-256);
        /* understand if we are getting the nearest integer */
        uint64_t tgt1,tgt2;
        tgt1=(uint64_t)privGetXtalFrequency()*((uint64_t)fdev_m+256);
        tgt2=(uint64_t)privGetXtalFrequency()*((uint64_t)fdev_m+1+256);
        fdev_m=((uint64_t)6291456000-tgt1>tgt2-(uint64_t)6291456000)?(fdev_m+1):(fdev_m);
      }
    }
  }

  /* write DATARATE mantissa and exponent */
  regs[0]=(dr_m>>8)&0xFF;
  regs[1]=(dr_m)&0xFF;
  regs[2]=mod_e;
  priv_ST_MANUF_WriteRegisters(0x0E,3,regs);

  /* write FDEV mantissa and exponent */
  /* here the exponent is in | with 0x80 to enable the digital smooth of the ramps */
  regs[0]=fdev_e|0x80;
  regs[1]=fdev_m;
  priv_ST_MANUF_WriteRegisters(0x11,2,regs);

  priv_ST_MANUF_Get_Ramps_Settings(&st_manuf_context->ramps_settings);
}

/* Function to generate PN9 */
void pn9_next(uint16_t *last)
{
  uint16_t retval;
  retval =  (((*last & 0x20) >> 5) ^ *last) << 8;
  retval |= (*last >> 1) & 0xff;
  *last = retval & 0x1ff;
}

uint16_t pn9_next_byte(uint16_t state)
{
  int i;
  for (i=0; i<8; i++) {
    pn9_next(&state);
  }
  return state;
}

/* Function to transmit a single bit */
static void priv_ST_MANUF_tx_rf_dbpsk_single_bit(uint8_t bit)
{
  if(bit==0)
  {
    /* Give FDEV a peak in the FDEV_PEAK position.
    This value should be the opposite of the last one. */
    priv_ST_MANUF_generateFIFORampsBuffer(FIFO_RAMP_FAST, &rampBuffer[0], &bfSize, &st_manuf_context->ramps_settings);
    bSwap=(bSwap==st_manuf_context->ramps_settings.fdev_neg)?(st_manuf_context->ramps_settings.fdev_pos):(st_manuf_context->ramps_settings.fdev_neg);
    rampBuffer[82-32]=bSwap;
    priv_ST_MANUF_SpiRaw_Ramp(bfSize, rampBuffer, NULL, 1);
  }
  else
  {
    /* If the bit to be transmitted is '1' --> proceed with a constant
    pattern that does not change the instantaneous frequency and keeps power constant to max.
    fifo_const_fast stores this one. */
    priv_ST_MANUF_generateFIFORampsBuffer(FIFO_CONST_FAST, &rampBuffer[0], &bfSize, &st_manuf_context->ramps_settings);
    priv_ST_MANUF_SpiRaw_Ramp(bfSize, rampBuffer, NULL, 1);
  }
}

st_fifo_state_t ST_RF_API_GetFIFOState(void){
  return _s2lpFIFOState;
}

/* Transmission state machine */
static void priv_ST_MANUF_Transmission_Tick(void)
{
  _s2lpFIFOState = ST_FIFO_STATE_FILLING;

  switch(st_manuf_context->tx_packet_struct.tx_state)
  {
    /*
    When the state machine is here means that we have loaded the very first part of the RAMP_UP
    and we need to load the second part (the values of this part is stored into the variable into the fifo_start_ramp_up_2)
    */
  case ST_TX_STATE_RAMP_UP_2:
    {
	/* load the TX_FIFO */
	priv_ST_MANUF_generateFIFORampsBuffer(FIFO_RAMP_UP_2, &rampBuffer[0], &bfSize, &st_manuf_context->ramps_settings);
	priv_ST_MANUF_SpiRaw_Ramp(bfSize, rampBuffer, NULL, 1);
	/* prepare the next state through the following operations: */

	if (st_manuf_context->tx_packet_struct.continuous_tx_monarch_flag==1)
	{
	  /* -  starting from the most significative bit (bit 8) */
	  st_manuf_context->tx_packet_struct.bit_index=8;
	  /* -  set the tx_state to TX_STATE DATA to start to modulate the data bits the next time */
	  st_manuf_context->tx_packet_struct.tx_state=ST_TX_CONTINUOS_BPSK;
	}
	else
	{
	  /* -  we will need to take the first byte (index 0 of the data array) */
	  st_manuf_context->tx_packet_struct.byte_index=0;
	  /* -  starting from the most significative bit (bit 7) */
	  st_manuf_context->tx_packet_struct.bit_index=7;
	  /* -  set the tx_state to TX_STATE DATA to start to modulate the data bits the next time */
	  st_manuf_context->tx_packet_struct.tx_state=ST_TX_STATE_DATA;
	}
    }
    break;

  case ST_TX_CONTINUOS_BPSK:
    {
	uint8_t bit=(st_manuf_context->tx_packet_struct.current_pn9>>st_manuf_context->tx_packet_struct.bit_index) & 0x01;
	priv_ST_MANUF_tx_rf_dbpsk_single_bit(bit);

	if(st_manuf_context->tx_packet_struct.bit_index==0)
	{
	  /* if yes restore the bit "pointer" to the maximum */
	  st_manuf_context->tx_packet_struct.bit_index=8;
	  /*GENERATE NEXT pn9()*/
	  st_manuf_context->tx_packet_struct.current_pn9 = pn9_next_byte(st_manuf_context->tx_packet_struct.current_pn9);
	}

	else st_manuf_context->tx_packet_struct.bit_index--;

    }
    break;

  case ST_TX_STATE_DATA:
    {

	/* extract the bit to modulate from the array pointed by data_to_send */
	uint8_t bit=(st_manuf_context->tx_packet_struct.data_to_send[st_manuf_context->tx_packet_struct.byte_index]>>st_manuf_context->tx_packet_struct.bit_index)&0x01;
	/* the sigfox protocol says that a bit '0' should be represented by a phase inversion */

	priv_ST_MANUF_tx_rf_dbpsk_single_bit(bit);

	/* prepare the next data: first check if we need to change byte*/
	if(st_manuf_context->tx_packet_struct.bit_index==0)
	{
	  /* if yes restore the bit "pointer" to the maximum */
	  st_manuf_context->tx_packet_struct.bit_index=7;

	  /* increase the byte pointer */
	  st_manuf_context->tx_packet_struct.byte_index++;

	  /* check if data is over */
	  if(st_manuf_context->tx_packet_struct.byte_index==st_manuf_context->tx_packet_struct.data_to_send_size)
	  {
	    /* in this case move the state machine to the RAMP_DOWN_1 state
	    so that the next time we will start to ramp down.*/
	    st_manuf_context->tx_packet_struct.byte_index=0;
	    st_manuf_context->tx_packet_struct.tx_state=ST_TX_STATE_RAMP_DOWN_1;
	  }
	}
	else
	{
	  /* if we don't need to change byte just decrease the bit pointer to go to the next bit */
	  st_manuf_context->tx_packet_struct.bit_index--;
	}
    }
    break;

  case ST_TX_STATE_RAMP_DOWN_1:
    /* store the 1st part of the TX RAMP DOWN pattern */
    priv_ST_MANUF_generateFIFORampsBuffer(FIFO_RAMP_DOWN_1, &rampBuffer[0], &bfSize, &st_manuf_context->ramps_settings);
    priv_ST_MANUF_SpiRaw_Ramp(bfSize, rampBuffer, NULL, 1);
    /* move the state to store the second part */
    st_manuf_context->tx_packet_struct.tx_state=ST_TX_STATE_RAMP_DOWN_2;
    break;

  case ST_TX_STATE_RAMP_DOWN_2:
    /* store the 2nd part of the TX RAMP DOWN pattern */
    priv_ST_MANUF_generateFIFORampsBuffer(FIFO_RAMP_DOWN_2, &rampBuffer[0], &bfSize, &st_manuf_context->ramps_settings);
    priv_ST_MANUF_SpiRaw_Ramp(bfSize, rampBuffer, NULL, 1);
    /* move the state to store the third part... */
    st_manuf_context->tx_packet_struct.tx_state=ST_TX_STATE_RAMP_DOWN_3;
    break;

  case ST_TX_STATE_RAMP_DOWN_3:
    /* notice that the 3rd part of the ramp is just a sequence of zeroes used as a padding
    to wait the fifo_ramp_down_2 is over */
    priv_ST_MANUF_SpiRaw_Ramp(66, (uint8_t*)zeroes, NULL, 1);

    /* the next state will be TX_STATE_STOP to shut off the transmitter */
    st_manuf_context->tx_packet_struct.tx_state=ST_TX_STATE_STOP;
    break;

  case ST_TX_STATE_STOP:

    /* give the ABORT command to stop the transmitter */
    ST_RF_API_StopRxTx();
    /* give the FLUSH_TX command to flush the TX FIFO*/
    CMD_STROBE_FTX();
    /* disable the IRQ on the MCU side */
    ST_MCU_API_GpioIRQ(SFX_FALSE, SFX_TRUE);
    /* reset the SM state */
    st_manuf_context->tx_packet_struct.tx_state=ST_TX_STATE_NONE;
    /* notify to the MANUF_API_rf_send that we are done setting the s2lp_irq_raised flag */
    st_manuf_context->s2lp_irq_raised=1;
    break;
  }
}

/* Function used both for BPSK MOD and CONTINUOS BPSK */
static void priv_ST_MANUF_rf_load_first_ramp_up()
{
  uint8_t tmp;
  /* TX FIFO flush */
  CMD_STROBE_FTX();

  /* fill the 1st part of the FIFO */
  priv_ST_MANUF_SpiRaw_Ramp(18, (uint8_t*)zeroes, NULL,0);
  priv_ST_MANUF_generateFIFORampsBuffer(FIFO_RAMP_UP_1, &rampBuffer[0], &bfSize, &st_manuf_context->ramps_settings);
  priv_ST_MANUF_SpiRaw_Ramp(bfSize, rampBuffer, NULL, 0);

  /* GPIO interrupt on S2-LP side */
  tmp=0x32;
  priv_ST_MANUF_WriteRegisters(S2LP_GPIO_IRQ_PIN, 1, &tmp);

  /* S2-LP IRQ on MCU side */
  ST_MCU_API_GpioIRQ(SFX_TRUE, SFX_TRUE);

  /* manuf_state to TX */
  st_manuf_context->manuf_state=ST_MANUF_STATE_TX;

  /* next TX state is the 2nd part of the ramp-up */
  st_manuf_context->tx_packet_struct.tx_state=ST_TX_STATE_RAMP_UP_2;
}

static void priv_ST_MANUF_rf_modulation_dbpsk(uint8_t* stream, uint8_t size)
{
  st_manuf_context->tx_packet_struct.continuous_tx_monarch_flag=0; //The transmission will be a packet and not PN9

  /* save the current pointer to data and size */
  st_manuf_context->tx_packet_struct.data_to_send=stream;
  st_manuf_context->tx_packet_struct.data_to_send_size=size;

  //SET GPIO to receive interrupt and Send first ramp in the FIFO
  priv_ST_MANUF_rf_load_first_ramp_up();
  /* give the TX command: from now on the device will start to transmit */
  ST_RF_API_StartTx();
  /* use the s2lp_irq_raised flag to understand when the function should return.
  All the FIFO management will be done into the priv_ST_MANUF_Transmission_Tick (generated by the ST_MANUF_S2LP_Exti_CB() fcn)*/
  st_manuf_context->s2lp_irq_raised=0;
  while(!st_manuf_context->s2lp_irq_raised){
    ST_MCU_API_WaitForInterrupt();
  }
  /* if we are here, we have finished the transmission */
  st_manuf_context->s2lp_irq_raised=0;

  /* reset the manuf_state to IDLE */
  st_manuf_context->manuf_state=ST_MANUF_STATE_IDLE;
}

static void priv_ST_MANUF_rx_rf_init(void)
{
  uint64_t tgt1,tgt2;
  uint32_t f_dig=privGetXtalFrequency();
  uint16_t dr_m;
  uint8_t mod_e,fdev_e,fdev_m,tmp;
  uint8_t regs[3];
  /* packet setting registers */
  uint8_t pckt_setting[]={0,0,0,0,15};

  if(f_dig>DIG_DOMAIN_XTAL_THRESH) {
    f_dig >>= 1;
  }

  /* modulation is 2GFSK01 @600bps| DR EXPONENT = 1 */
  mod_e=0x20|0x01;
  /* dr_num=(2**32)*600 */
  dr_m=(uint16_t)((uint64_t)0x25800000000/f_dig-65536);
  /* understand if we are getting the nearest integer */
  tgt1=(uint64_t)f_dig*((uint64_t)dr_m+65536);
  tgt2=(uint64_t)f_dig*((uint64_t)dr_m+1+65536);
  dr_m=((uint64_t)0x25800000000-tgt1>tgt2-(uint64_t)0x25800000000)?(dr_m+1):(dr_m);

  fdev_e=0;
  /* fdev_num=((2**22)*800) - FDEV=800Hz */
  fdev_m=(uint8_t)((uint64_t)3355443200/privGetXtalFrequency());
  /* understand if we are getting the nearest integer */
  tgt1=(uint64_t)privGetXtalFrequency()*((uint64_t)fdev_m);
  tgt2=(uint64_t)privGetXtalFrequency()*((uint64_t)fdev_m+1);
  fdev_m=((uint64_t)3355443200-tgt1>tgt2-(uint64_t)3355443200)?(fdev_m+1):(fdev_m);

  uint8_t if_regs[2];

  if_regs[0] = (uint8_t)(((uint64_t)7372800000/privGetXtalFrequency())-100);
  if_regs[1] = (uint8_t)(((uint64_t)7372800000/f_dig)-100);

  priv_ST_MANUF_WriteRegisters(0x09, 2, if_regs);

  /* write DATARATE mantissa and exponent */
  regs[0]=(dr_m>>8)&0xFF;
  regs[1]=(dr_m)&0xFF;
  regs[2]=mod_e;
  priv_ST_MANUF_WriteRegisters(0x0E,3,regs);

  /* write FDEV mantissa and exponent */
  regs[0]=fdev_e;
  regs[1]=fdev_m;
  priv_ST_MANUF_WriteRegisters(0x11,2,regs);

  /* channel filter */

#ifdef MON_REF_DES
  tmp=0x18; //3.3 KHz - Since there is LNA, we are able to receive even with a larger filter.
#else
if (f_dig>24500000) /*CHFILTER must be multiplied for Fdig/26e6 to obtain the actual value*/
  tmp=0x88; //2.1 KHz
else
  tmp=0x68;
#endif

  priv_ST_MANUF_WriteRegisters(0x13,1,&tmp);

  /* settings of the packet (CRC, FEC, WHIT, ...) + packet length to 15*/
  priv_ST_MANUF_WriteRegisters(0x2E, 5, pckt_setting);

  /* SYNC LEN */
  pckt_setting[0]=0x40;
  priv_ST_MANUF_WriteRegisters(0x2B, 1, pckt_setting);

  /* SYNC WORD 16 bits 0xB227 */
  pckt_setting[0]=0x27;
  pckt_setting[1]=0xB2;
  priv_ST_MANUF_WriteRegisters(0x35, 2, pckt_setting);

  /* SYNC WORD LENGTH is 16bits */
  pckt_setting[0]=0x40;
  pckt_setting[1]=0x00;
  priv_ST_MANUF_WriteRegisters(0x39, 2, pckt_setting);

  /* equ ctrl and cs blank */
  tmp=0x00;
  priv_ST_MANUF_WriteRegisters(0x1f,1,&tmp);

  /* RSSI thr */
  tmp=0x07;
  priv_ST_MANUF_WriteRegisters(0x18,1,&tmp);

  /* CLK rec fast */
  tmp=0x70;
  priv_ST_MANUF_WriteRegisters(0x21,1,&tmp);

  /* CLK rec slow */
  tmp=0x20;
  priv_ST_MANUF_WriteRegisters(0x20,1,&tmp);

  /* AFC */
  tmp=0x00;
  priv_ST_MANUF_WriteRegisters(0x14,1,&tmp);

  /* SMPS switch to 0x8800 - old */
  /* SMPS switch to 0x87FC - new */
  tmp=0x88;
  //tmp=0x87;
  priv_ST_MANUF_WriteRegisters(0x76, 1, &tmp);
  tmp=0x00;
  //tmp=0xFC;
  priv_ST_MANUF_WriteRegisters(0x77, 1, &tmp);

  st_manuf_context->tx_is_ready=0;
}

#ifdef MONARCH_FEATURE_ENABLED

static void priv_ST_MANUF_rx_monarch_rf_init(void)
{
  PRINTF("priv_ST_MANUF_rx_monarch_rf_init IN \n\r");

  /*It Informs trough ST_RF_API_Get_Continuous_TX_or_MONARCH_Scan_Flag, the mcu api that monarch scan is ongoing*/
  st_manuf_context->tx_packet_struct.continuous_tx_monarch_flag=1;

  uint64_t tgt1,tgt2;
  uint32_t f_dig=0;
  uint16_t dr_m=0;

  f_dig=privGetXtalFrequency();
  /*The digital frequency is half of xtal frequancy for high freq xtals cuts */
  if(f_dig > DIG_DOMAIN_XTAL_THRESH) f_dig >>= 1;

  /* SET THE IF TO 300 KHz - It is necessary especially for low frequancy xtals (Both IF equal) */
  uint8_t if_regs[2];
  if_regs[0] = (uint8_t)(((uint64_t)7372800000/privGetXtalFrequency())-100);
  if_regs[1] = (uint8_t)(((uint64_t)7372800000/f_dig)-100);
  priv_ST_MANUF_WriteRegisters(0x09, 2, if_regs);

  /* DATARATE MANTISSA COMPUTATION FOR EXP=6 */
  dr_m=(uint16_t)(((uint64_t)MONARCH_DATARATE*134217728)/f_dig-65536);
  /* understand if we are getting the nearest integer */
  tgt1=(uint64_t)f_dig*((uint64_t)dr_m+65536);
  tgt2=(uint64_t)f_dig*((uint64_t)dr_m+1+65536);
  dr_m=((uint64_t)((uint64_t) MONARCH_DATARATE*134217728)-tgt1>tgt2-(uint64_t)((uint64_t) MONARCH_DATARATE*134217728))?(dr_m+1):(dr_m);

  /* WRITE DATARATE + MOD TYPE REGS */
  uint8_t regs[3];
  regs[0]=(dr_m>>8)&0xFF; //MOD4 DATA_RATE_M[15:8]
  regs[1]=(dr_m)&0xFF;    //MOD3 DATA_RATE_M[7:0]
  regs[2]=0x56;           //MOD2 MOD TYPE [7:4] + DATA_RATE_E [3:0] = OOK + EXP=6
  priv_ST_MANUF_WriteRegisters(0x0E,3,regs);

  // Channel filter
  regs[0]=0x84;  //CHFLT MANTISSA [7:4] +EXPONENT [3:0] 20Khz
  priv_ST_MANUF_WriteRegisters(0x13,1,regs);

  // OOK decay 0 + RSSI TH
  regs[0]=0xE0; // DECAY
  regs[1]=0x15; // RSSI TH old 18
  priv_ST_MANUF_WriteRegisters(0x17,2, regs);

  // S2LP GPIO3 Configuration
#ifdef MONARCH_GPIO_SAMPLING
  regs[0]=0x42; // GPIO3_CONF RX data output, OOK Output
#else
  /* manuf_state to MONARCH SCAN to mux gpio it handler */
  st_manuf_context->manuf_state=ST_MANUF_STATE_MONARCH_SCAN;
  regs[0]=0x3A; // GPIO3_CONF: TX/RX FIFO ALMOST FULL FLAG
#endif
  priv_ST_MANUF_WriteRegisters(0x03,1, regs);

  //SET FIFO
#ifndef MONARCH_GPIO_SAMPLING
  //Set Almost full Mux Sel to Select RX fifo
  priv_ST_MANUF_ReadRegisters(0x39, 1, regs);
  regs[0] |= 0x04;
  priv_ST_MANUF_WriteRegisters(0x39,1, regs); //PROTOCOL2 REG --> FIFO_GPIO_OUT_MUX_SEL = 1
#endif

  //DIRECT RX THROUGH GPIO/FIFO BYPASSING PKT HANDLER
#ifdef MONARCH_GPIO_SAMPLING
  regs[0]=0x20; //THROUGH GPIO
#else
  regs[0]=0x10; //THROUGH FIFO
#endif
  priv_ST_MANUF_WriteRegisters(0x2E,1, regs);
  //RX TIMEOUT 0 - TIMERS5
  regs[0]=0x00;
  priv_ST_MANUF_WriteRegisters(0x46,1, regs);

  //AGC Conf
  regs[0]=0xF0;
  //AGCCTRL5
  priv_ST_MANUF_WriteRegisters(0x19,1, regs);

  //AGC Conf, Philippe configuration
  regs[0]=0x00;
  //AGCCTRL4
  priv_ST_MANUF_WriteRegisters(0x1A,1, regs);

  PRINTF("priv_ST_MANUF_rx_monarch_rf_init OUT \n\r");
}

#endif

__weak void ST_RF_API_custom_setting(void)
{
}

/*!******************************************************************
* \fn sfx_u8 RF_API_init(sfx_rf_mode_t rf_mode)
* \brief Init and configure Radio link in RX/TX
*
* [RX Configuration]
* To receive Sigfox Frame on your device, program the following:
*  - Preamble  : 0xAAAAAAAAA
*  - Sync Word : 0xB227
*  - Packet of the Sigfox frame is 15 bytes length.
*
* \param[in] sfx_rf_mode_t rf_mode         Init Radio link in Tx or RX
* \param[out] none
*
* \retval SFX_ERRNONE:              No error
* \retval RF_ERR_API_INIT:          Init Radio link error
*******************************************************************/
sfx_u8 RF_API_init(sfx_rf_mode_t rf_mode)
{
  PRINTF("RF_API_init IN (rf_mode=%d)\n\r",rf_mode);
  sfx_u8 tmp;

  if(rf_mode==SFX_RF_MODE_TX && st_manuf_context->tx_is_ready)
  {
    st_manuf_context->tx_packet_struct.tx_state=ST_TX_STATE_NONE;
    PRINTF("RF_API_init fast OUT\n\r");
    return SFX_ERR_NONE;
  }

  ST_MCU_API_Shutdown(1);
  ST_MCU_API_Shutdown(0);

  if(st_manuf_context->tcxo_flag){
    tmp=0xB0;
    priv_ST_MANUF_WriteRegisters(0x6D,1,&tmp);
  }

  ST_MCU_API_GpioIRQ(SFX_FALSE, SFX_FALSE);

  if(privGetXtalFrequency()<30000000)
  {
    /* digital divider - set the bit to 1 only if xtal<30MHz so that the divider is disabled + Frequency drift mitigation*/
    tmp=0x3E;
    priv_ST_MANUF_WriteRegisters(0x6C,1,&tmp);
  }
  else
  {
    /* To mitigate freq drift use 0X2E */
    tmp=0x2E;
    priv_ST_MANUF_WriteRegisters(0x6C, 1, &tmp);
  }

  switch (rf_mode)
  {
  case SFX_RF_MODE_CS200K_RX:
    /* configure the RF IC into sensing 200KHz bandwidth to be able to read out RSSI level
    RSSI level will outputed during the wait_for_clear_channel api */
  case SFX_RF_MODE_CS300K_RX:
    /* configure the RF IC into sensing 300KHz bandwidth to be able to read out RSSI level
    This is possible to make this carrier sense in 2 * 200Kz if you respect the regulation time for listening
    RSSI level will outputed during the wait_for_clear_channel api */
    {
	uint8_t tmp,if_regs[2];
	uint32_t f_dig=privGetXtalFrequency();

	if(f_dig>DIG_DOMAIN_XTAL_THRESH) {
	  f_dig >>= 1;
	}
	if_regs[0] = (uint8_t)(((uint64_t)7372800000/privGetXtalFrequency())-100);
	if_regs[1] = (uint8_t)(((uint64_t)7372800000/f_dig)-100);
	priv_ST_MANUF_WriteRegisters(0x09, 2, if_regs);
	/* channel filter */
	tmp=0x81; /* 200kHz+ filter */
	if(rf_mode==SFX_RF_MODE_CS300K_RX)
	{
	  tmp=0x51;  /* 300kHz+ filter */
	}
	priv_ST_MANUF_WriteRegisters(0x13,1,&tmp);
	tmp=0x20;
	priv_ST_MANUF_WriteRegisters(0x2E,1,&tmp);

    }
    /* here the lack of a break is intetional because we should do the case SFX_RF_MODE_TX also */
  case SFX_RF_MODE_TX :
    priv_ST_MANUF_tx_rf_init();
    break;
  case SFX_RF_MODE_RX :
    priv_ST_MANUF_rx_rf_init();
    break;
#ifdef MONARCH_FEATURE_ENABLED
  case  SFX_RF_MODE_MONARCH:
    priv_ST_MANUF_rx_monarch_rf_init();
    break;
#endif
  default :
    break;
  }

  _s2lpFIFOState = ST_FIFO_STATE_WAITING_UNDERFLOW;
  priv_ST_MANUF_Get_Ramps_Settings(&st_manuf_context->ramps_settings);
  ST_RF_API_custom_setting();

  return SFX_ERR_NONE;
}

/*!******************************************************************
* \fn sfx_u8 RF_API_stop(void)
* \brief Close Radio link
*
* \param[in] none
* \param[out] none
*
* \retval SFX_ERR_NONE:              No error
* \retval RF_ERR_API_STOP:           Close Radio link error
*******************************************************************/
sfx_u8 RF_API_stop(void)
{
  PRINTF("RF_API_stop IN\n\r");

  /* give an abort command (just for safety) */
  ST_RF_API_StopRxTx();

  /* shut down the radio */
  ST_MCU_API_Shutdown(1);

  //To be verified, verify if for every condition the monarch end with RF_API_stop
#ifndef MONARCH_GPIO_SAMPLING //Only for monarch fifo feature
  if (st_manuf_context->manuf_state==ST_MANUF_STATE_MONARCH_SCAN)
    st_manuf_context->manuf_state=ST_MANUF_STATE_IDLE;
#endif

  st_manuf_context->s2lp_irq_raised=0;

  st_manuf_context->tx_is_ready=0;

  PRINTF("RF_API_stop OUT\n\r");

  return SFX_ERR_NONE;
}

/*!******************************************************************
* \fn sfx_u8 RF_API_send(sfx_u8 *stream, sfx_modulation_type_t type, sfx_u8 size)
* \brief BPSK Modulation of data stream
* (from synchro bit field to CRC)
*
* NOTE : during this function, the voltage_tx needs to be retrieved and stored in
*        a variable to be returned into the MCU_API_get_voltage_and_temperature or
*        MCU_API_get_voltage functions.
*
* \param[in] sfx_u8 *stream                Complete stream to modulate
* \param[in]sfx_modulation_type_t          Type of the modulation ( enum with baudrate and modulation information)
* \param[in] sfx_u8 size                   Length of stream
* \param[out] none
*
* \retval SFX_ERR_NONE:                    No error
* \retval RF_ERR_API_SEND:                 Send data stream error
*******************************************************************/
sfx_u8 RF_API_send(sfx_u8 *stream, sfx_modulation_type_t type, sfx_u8 size)
{
  PRINTF("RF_API_send IN\n\r");

  PRINTF("FTS: [");
  for(uint8_t i=0;i<size;i++)
  {
    PRINTF("%.2X",stream[i]);
  }
  PRINTF("]\n\r");

  if(type==SFX_NO_MODULATION || st_manuf_context->manuf_state!=ST_MANUF_STATE_IDLE)
    return RF_ERR_API_SEND;

  /* configure the modem according to the modulation (100bps, 600bps) */
  priv_ST_MANUF_tx_rf_dbpsk_init(type);

  /* start the modulation of the data stream */
  priv_ST_MANUF_rf_modulation_dbpsk(stream, size);

#ifdef MONARCH_CLI_TESTS
  printf("{{(SigfoxSendBPSK)} API call...{value:");
  for(uint8_t i=0;i<size;i++)
  {
    printf("%.2X",stream[i]);
  }
  printf("}}\n\r");
#endif
  PRINTF("RF_API_send OUT\n\r");

  return SFX_ERR_NONE;
}

/*!******************************************************************
* \fn sfx_u8 RF_API_start_continuous_transmission (sfx_modulation_type_t type)
* \brief Generate a signal with modulation type. All the configuration ( Init of the RF and Frequency have already been executed
*        when this function is called.
*
* \param[in] sfx_modulation_type_t         Type of the modulation ( enum with baudrate and modulation information is contained in sigfox_api.h)
*
* \retval SFX_ERR_NONE:                                 No error
* \retval RF_ERR_API_START_CONTINUOUS_TRANSMISSION:     Continuous Transmission Start error
*******************************************************************/
sfx_u8 RF_API_start_continuous_transmission(sfx_modulation_type_t type)
{
  PRINTF("RF_API_start_continuous_transmission IN\n\r");

  if(st_manuf_context->manuf_state!=ST_MANUF_STATE_IDLE)
    return RF_ERR_API_SEND;

  // Make an infinite BPSK 100/600bps modulation on the RF IC at the frequency given by the RF_API_change_frequency()
  // If BPSK modulation configure based on datarate

  if (type==SFX_DBPSK_100BPS || type==SFX_DBPSK_600BPS)
  {
    /* S2-LP IRQ on MCU side */
    ST_MCU_API_GpioIRQ(SFX_TRUE, SFX_TRUE);

    st_manuf_context->tx_packet_struct.continuous_tx_monarch_flag=1; //The transmission will be a PN9 and no packets
    st_manuf_context->tx_packet_struct.current_pn9=PN9_INITIALIZER;
    priv_ST_MANUF_tx_rf_dbpsk_init(type);

    // Set GPIO to receive interrupt and Send first ramp in the FIFO
    priv_ST_MANUF_rf_load_first_ramp_up();

    /* Give the TX command: from now on the device will start to transmit */
    ST_RF_API_StartTx();
  }

  // Configure the RF IC into pure carrier CW : no modulation
  // this mode is available on many RF ICs for type approval tests or manufacturing tests.
  // the frequency is chosen in the RF_API_change_frequency by the sigfox lib
  // SPI_DRV_write(CW)
  else if (type==SFX_NO_MODULATION)
  {
    sfx_u8 tmp;

    ST_MCU_API_GpioIRQ(SFX_FALSE, SFX_FALSE);

    // MOD register to Save Datarate and pu
    priv_ST_MANUF_ReadRegisters(0x10, 1, &tmp);
    tmp &= (~0xF0);
    tmp |= 0x70;
    priv_ST_MANUF_WriteRegisters(0x10, 1, &tmp);

    // Set Power PA_POWER8
#ifdef MON_REF_DES
    if (st_manuf_context->pa_flag == 0)
	tmp=1+st_manuf_context->power_reduction;
    else
	tmp=1+5+st_manuf_context->power_reduction;
#else
    tmp=1+st_manuf_context->power_reduction;
#endif

    priv_ST_MANUF_WriteRegisters(0x5A, 1, &tmp);

    st_manuf_context->manuf_state=ST_MANUF_STATE_TX;

    ST_RF_API_StartTx();
  }

  PRINTF("RF_API_start_continuous_transmission OUT\n\r");

  return SFX_ERR_NONE;
}

/*!******************************************************************
* \fn sfx_u8 RF_API_stop_continuous_transmission (void)
* \brief Stop the current continuous transmisssion
*
* \retval SFX_ERR_NONE:                                 No error
* \retval RF_ERR_API_STOP_CONTINUOUS_TRANSMISSION:      Continuous Transmission Stop error
*******************************************************************/
sfx_u8 RF_API_stop_continuous_transmission (void)
{
  PRINTF("RF_API_stop_continuous_transmission IN\n\r");

  ST_RF_API_StopRxTx();

  st_manuf_context->manuf_state=ST_MANUF_STATE_IDLE;

  if (st_manuf_context->tx_packet_struct.continuous_tx_monarch_flag)
    ST_MCU_API_GpioIRQ(SFX_FALSE, SFX_FALSE);

  PRINTF("RF_API_stop_continuous_transmission OUT\n\r");

  return SFX_ERR_NONE;
}

/*!******************************************************************
* \fn sfx_u8 RF_API_change_frequency(sfx_u32 frequency)
* \brief Change synthesizer carrier frequency
*
* \param[in] sfx_u32 frequency             Frequency in Hz to program in the radio chipset
* \param[out] none
*
* \retval SFX_ERR_NONE:                    No error
* \retval RF_ERR_API_CHANGE_FREQ:          Change frequency error
*******************************************************************/
sfx_u8 RF_API_change_frequency(sfx_u32 frequency)
{
  PRINTF("RF_API_change_frequency IN %d\n\r",frequency);

  uint8_t tmp[4];
  uint32_t synth;

  synth=((uint64_t)2097152*frequency/privGetXtalFrequency());
  /* understand if we are getting the nearest integer */
  uint64_t tgt1,tgt2;
  tgt1=(uint64_t)privGetXtalFrequency()*((uint64_t)synth);
  tgt2=(uint64_t)privGetXtalFrequency()*((uint64_t)synth+1);
  synth=((uint64_t)2097152*frequency-tgt1>tgt2-(uint64_t)2097152*frequency)?(synth+1):(synth);

  /* CHARGE PUMP */
  uint32_t vcofreq = frequency*4;
  uint8_t cp_isel,pfd_split;

  /* Set the correct charge pump word */
  if(vcofreq>=(uint64_t)3600000000) {
    if(privGetXtalFrequency()>DIG_DOMAIN_XTAL_THRESH) {
	cp_isel = 0x02;
	pfd_split = 0;
    }
    else {
	cp_isel = 0x01;
	pfd_split = 1;
    }
  }
  else {
    if(privGetXtalFrequency()>DIG_DOMAIN_XTAL_THRESH) {
	cp_isel = 0x03;
	pfd_split = 0;
    }
    else {
	cp_isel = 0x02;
	pfd_split = 1;
    }
  }

  priv_ST_MANUF_ReadRegisters(0x65, 1, tmp);
  tmp[0] &= (~0x04);
  tmp[0] |= (pfd_split<<2);
  priv_ST_MANUF_WriteRegisters(0x65, 1, tmp);

  tmp[0] = (((uint8_t)(synth>>24)) & 0x0F) | (cp_isel<<5);
  tmp[1] = (uint8_t)(synth>>16);
  tmp[2] = (uint8_t)(synth>>8);
  tmp[3] = (uint8_t)synth;

  priv_ST_MANUF_WriteRegisters(0x05, 4, tmp);

  PRINTF("RF_API_change_frequency OUT (SYNT=0x%x)\n\r",synth);

  return SFX_ERR_NONE;
}

/*!******************************************************************
* \fn sfx_u8 RF_API_wait_frame(sfx_u8 *frame, sfx_s16 *rssi, sfx_rx_state_enum_t * state)
* \brief Get all GFSK frames received in Rx buffer, structure of
* frame is : Synchro bit + Synchro frame + 15 Bytes.<BR> This function must
* be blocking state since data is received or timer of 25 s has elapsed.
*
* - If received buffer, function returns SFX_ERR_MANUF_NONE then the
*   library will try to decode frame. If the frame is not correct, the
*   library will recall RF_API_wait_frame .
*
* - If 25 seconds timer has elapsed, function returns
*   SFX_ERR_MANUF_WAIT_FRAME_TIMEOUT then library will stop receive
*   frame phase.
*
* \param[in] none
* \param[out] sfx_s8 *frame                  Receive buffer
* \param[out] sfx_s16 *rssi                  Chipset RSSI
* Warning: This is the 'raw' RSSI value. Do not add 100 as made
* in Library versions 1.x.x
* Resolution: 1 LSB = 1 dBm
*
* \param[out] sfx_rx_state_enum_t state      Indicate the final state of the reception. Value can be TIMEOUT or PASSED
*                                            if a frame has been received,  as per defined in sigfox_api.h file.
*
* \retval SFX_ERR_NONE:                      No error
* \retval RF_ERR_API_WAIT_FRAME_TIMEOUT:     Wait frame error
*******************************************************************/
sfx_u8 RF_API_wait_frame(sfx_u8 *frame, sfx_s16 *rssi, sfx_rx_state_enum_t * state)
{
  sfx_u8 sync_detected=0;
  sfx_u8 n_bytes, tmp[4]={0,0,0,0};

  PRINTF("RF_API_wait_frame IN\n\r");

  /* enable the RX DATA READY interrupt */
  tmp[3]=0x01;
  /* enable the VALID SYNC interrupt */
  tmp[2]=0x20;
  priv_ST_MANUF_WriteRegisters(0x50,4,tmp);

  /* GPIO configuration: IRQ on S2-LP pin */
  tmp[0]=0x02;
  priv_ST_MANUF_WriteRegisters(S2LP_GPIO_IRQ_PIN, 1, tmp);

  /* enable the GPIO interrupt on the MCU side - configure the MCU to sense the falling edge */
  ST_MCU_API_GpioIRQ(SFX_TRUE, SFX_FALSE);

  /* RX FIFO flush */
  CMD_STROBE_FRX();

  /* cleanup the IRQ STATUS registers */
  priv_ST_MANUF_ReadRegisters(0xFA,4,tmp);

  /* cleanup the IRQ flag */
  st_manuf_context->s2lp_irq_raised=0;

  /* set the manuf state to RX */
  st_manuf_context->manuf_state=ST_MANUF_STATE_RX;

  /* RX strobe command to the S2-LP */
  ST_RF_API_StartRx();

  while((!st_manuf_context->api_timer_raised) || sync_detected)
  {
    /* hook the wait for interrupt function */
    ST_MCU_API_WaitForInterrupt();

    if(st_manuf_context->s2lp_irq_raised)
    {
	st_manuf_context->s2lp_irq_raised=0;

	/* read the IRQ STATUS register */
	priv_ST_MANUF_ReadRegisters(0xFA,4,tmp);

	/* check the RX_DATA_READY interrupt */
	if(tmp[3]&0x01)
	{
	  /* -> if we get here we have some data info the RX FIFO */

	  /* read the num of bytes stored into the RX FIFO */
	  priv_ST_MANUF_ReadRegisters(0x90, 1, &n_bytes);

	  /* read the data stored into the RX FIFO */
	  priv_ST_MANUF_ReadFifo(n_bytes,frame);

	  /* read the RSSI value captured at the end of the SYNC word detection of the received packet */
	  priv_ST_MANUF_ReadRegisters(0xA2, 1, &st_manuf_context->last_rssi_reg);

	  (*rssi)=((sfx_s8)st_manuf_context->last_rssi_reg)-146+st_manuf_context->rssi_offset;

	  /* disable the interrupt on the MCU side */
	  ST_MCU_API_GpioIRQ(SFX_FALSE, SFX_FALSE);

	  /* reset the ST_MANUF state to IDLE */
	  st_manuf_context->manuf_state=ST_MANUF_STATE_IDLE;

	  /* reception succesful */
	  (*state) = DL_PASSED;

	  PRINTF("RF_API_wait_frame OUT (ok)\n\r");

	  return SFX_ERR_NONE;
	}

	/* check the VALID_SYNC interrupt, this is needed to manage the case when
	the SYNC has been detected near the edge of the RX window */
	if(tmp[2]&0x20)
	{
	  sync_detected=1;

	  PRINTF("RF_API_wait_frame -> sync_detected\n\r");
	}
    }
  }

  /* stop the reception */
  ST_RF_API_StopRxTx();

  /* disable the interrupt on the MCU side */
  ST_MCU_API_GpioIRQ(SFX_FALSE, SFX_FALSE);

  /* reset the ST_MANUF state to IDLE */
  st_manuf_context->manuf_state=ST_MANUF_STATE_IDLE;

  (*state) = DL_TIMEOUT;

  PRINTF("RF_API_wait_frame OUT (fail)\n\r");

  /* reception failed due to RX timeout */
  return SFX_ERR_NONE;
}

/*!******************************************************************
* \fn sfx_u8 RF_API_wait_for_clear_channel (sfx_u8 cs_min, sfx_u8 cs_threshold, sfx_rx_state_enum_t * state);
* \brief This function is used in ARIB standard for the Listen Before Talk
*        feature. It listens on a specific frequency band initialized through the RF_API_init(), during a sliding window set
*        in the MCU_API_timer_start_carrier_sense().
*        If the channel is clear during the minimum carrier sense
*        value (cs_min), under the limit of the cs_threshold,
*        the functions returns with SFX_ERR_NONE (transmission
*        allowed). Otherwise it continues to listen to the channel till the expiration of the
*        carrier sense maximum window and then updates the state ( with timeout enum ).
*
* \param[in] none
* \param[out] sfx_u8 cs_min                  Minimum Carrier Sense time in ms.
* \param[out] sfx_s8 cs_threshold            Power threshold limit to declare the channel clear.
*                                            i.e : cs_threshold value -80dBm in Japan / -65dBm in Korea
* \param[out] sfx_rx_state_enum_t state      Indicate the final state of the carrier sense. Value can be DL_TIMEOUT or PASSED
*                                            as per defined in sigfox_api.h file.
*
* \retval SFX_ERR_NONE:                      No error
*******************************************************************/
sfx_u8 RF_API_wait_for_clear_channel(sfx_u8 cs_min, sfx_s8 cs_threshold, sfx_rx_state_enum_t * state)
{
  PRINTF("RF_API_wait_for_clear_channel IN (cs_min=%d, cs_thr=%d)\n\r", cs_min, cs_threshold);

  uint8_t tmp[4]={0,0,0,0};
  uint32_t f_dig=privGetXtalFrequency();
  if(f_dig>DIG_DOMAIN_XTAL_THRESH) {
    f_dig >>= 1;
  }

  tmp[2]=0x40; /* RSSI_ABOVE_TH */
  tmp[0]=0x10; /* RX timeout */

  priv_ST_MANUF_WriteRegisters(0x50,4,tmp);

  tmp[0]=0x02;
  priv_ST_MANUF_WriteRegisters(S2LP_GPIO_IRQ_PIN, 1, tmp);

  ST_MCU_API_GpioIRQ(SFX_TRUE, SFX_FALSE);

  /* RSSI threshold setting */
  tmp[0]=(uint8_t)((sfx_s16)146+(sfx_s16)cs_threshold-st_manuf_context->rssi_offset-st_manuf_context->lbt_thr_offset);

  /* RSSI thr */
  priv_ST_MANUF_WriteRegisters(0x18,1,tmp);

  /* stop the timer at RSSI above THR */
  tmp[0]=0x80;
  priv_ST_MANUF_WriteRegisters(0x39,1,tmp);

  /* set the RX timeout */
  tmp[1]=(uint8_t)((((uint64_t)cs_min*f_dig/1000)/1210+1)/255);
  if(tmp[1]>1)
  {
    tmp[1]--;
  }
  else
  {
    tmp[1]=1;
  }

  tmp[0]=(uint8_t)((((uint64_t)cs_min*f_dig/1000)/1210+1)/(tmp[1]+1));

  PRINTF("REGISTER RXTIMERCNT=%d, PRESCALER=%d \n\r",tmp[0],tmp[1]);
  priv_ST_MANUF_WriteRegisters(0x46,2,tmp);

  st_manuf_context->manuf_state=ST_MANUF_STATE_WAIT_CLEAR_CH;

  (*state) = DL_PASSED;

  while(1)
  {
    CMD_STROBE_FRX();
    /* clean the IRQ STATUS registers */
    priv_ST_MANUF_ReadRegisters(0xFA,4,tmp);
    st_manuf_context->s2lp_irq_raised=0;

    /* enter in RX through the RX command */
    ST_RF_API_StartRx();

    while(!(st_manuf_context->s2lp_irq_raised || st_manuf_context->api_timer_channel_clear_raised))
    {
	ST_MCU_API_WaitForInterrupt();
    }
    if(st_manuf_context->s2lp_irq_raised)
    {
	st_manuf_context->s2lp_irq_raised=0;

	/* read the IRQ STATUS registers */
	priv_ST_MANUF_ReadRegisters(0xFA,4,tmp);

	/* check the IRQ_RSSI_ABOVE_TH flag */
	if(tmp[2]&0x40)
	{
	  ST_RF_API_StopRxTx();
	}
	/* check the IRQ_RX_TIMEOUT flag */
	else if(tmp[0]&0x10)
	{
	  (*state) = DL_PASSED;
	  break;
	}
    }
    if(st_manuf_context->api_timer_channel_clear_raised)
    {
	PRINTF("\t\t\t\t\t\t\t TIMEOUTn\r");
	st_manuf_context->api_timer_channel_clear_raised=0;
	(*state) = DL_TIMEOUT;
	break;
    }
  }

  if((*state) == DL_PASSED)
  {
    tmp[3]=0x00;tmp[2]=0x00; /* DISABLE all IRQs */
    tmp[1]=0x00;tmp[0]=0x00;
    priv_ST_MANUF_WriteRegisters(0x50,4,tmp);
  }
  else
  {
    ST_MCU_API_Shutdown(1);
    MCU_API_timer_stop_carrier_sense();
    st_manuf_context->tx_is_ready=0;
  }
  ST_MCU_API_GpioIRQ(SFX_FALSE, SFX_FALSE);

  st_manuf_context->manuf_state=ST_MANUF_STATE_IDLE;

  PRINTF("RF_API_wait_for_clear_channel OUT (passed=%d)\n\r",(*state));

  return SFX_ERR_NONE;
}

/*!******************************************************************
* \fn sfx_u8 RF_API_get_version(sfx_u8 **version, sfx_u8 *size)
* \brief Returns current RF API version
*
* \param[out] sfx_u8 **version                 Pointer to Byte array (ASCII format) containing library version
* \param[out] sfx_u8 *size                     Size of the byte array pointed by *version
*
* \retval SFX_ERR_NONE:                No error
* \retval RF_ERR_API_GET_VERSION:      Get Version error
*******************************************************************/
sfx_u8 RF_API_get_version(sfx_u8 **version, sfx_u8 *size)
{
  (*size) = ST_RF_API_VER_SIZE;
  (*version) = (sfx_u8*)ST_RF_API_VER;

  return SFX_ERR_NONE;
}

/* This is the callback that notifies that the MCU timer called
*  by the MANUF_API_timer_start started/has expired. */
void ST_RF_API_Timer_CB(sfx_u8 state)
{
  st_manuf_context->api_timer_raised=state;
}

/* This is the callback that notifies that the MCU timer started
*  by the MANUF_API_timer_start has expired. */
void ST_RF_API_Timer_Channel_Clear_CB(void)
{
  st_manuf_context->api_timer_channel_clear_raised=1;
}

/* This is the callback to be called each time an interrupt from S2-LP occurs */
void ST_RF_API_S2LP_IRQ_CB(void)
{
  /* If we are not transmitting the current implementation manages the actions to do
  *  with a flag (s2lp_irq_raised) that makes the functions waiting can be ticked on */
  if((st_manuf_context->manuf_state!=ST_MANUF_STATE_TX) && (st_manuf_context->manuf_state!=ST_MANUF_STATE_MONARCH_SCAN))
  {
    st_manuf_context->s2lp_irq_raised=1;
  }
#ifdef  MONARCH_FEATURE_ENABLED
#ifndef MONARCH_GPIO_SAMPLING
  else if (st_manuf_context->manuf_state==ST_MANUF_STATE_MONARCH_SCAN)
  {
    ST_MONARCH_API_AFTHR_GPIO_CB();
  }
#endif
#endif
  else
  {
    /* If we are transmitting, we have to tick the state machine for transmission
    so that the transmission actions (fill the TX FIFO according to the actual state)
    are done in this same context.
    The user can decide to call this function in the interrupt ISR or
    in the ST_MCU_API_WaitForInterrupt() function. */
    if (S2LPGetSpiInUse() == 0){
	priv_ST_MANUF_Transmission_Tick();
	_s2lpFIFOState = ST_FIFO_STATE_WAITING_UNDERFLOW;
    }
  }
}

/* RSSI offset as param */
sfx_u8 ST_RF_API_set_rssi_offset(int8_t rssi_off)
{
  st_manuf_context->rssi_offset=rssi_off;

  return SFX_ERR_NONE;
}

sfx_u8 ST_RF_API_get_rssi_offset(int8_t *rssi_off)
{
  (*rssi_off)=st_manuf_context->rssi_offset;

  return SFX_ERR_NONE;
}

/* XTAL FREQ as param */
sfx_u8 ST_RF_API_set_xtal_freq(sfx_u32 xtal)
{
  st_manuf_context->priv_xtal_freq = xtal;

  return SFX_ERR_NONE;
}

sfx_u8 ST_RF_API_get_xtal_freq(sfx_u32 *xtal)
{
  (*xtal)=st_manuf_context->priv_xtal_freq;

  return SFX_ERR_NONE;
}

/* LBT offset as param */
sfx_u8 ST_RF_API_set_lbt_thr_offset(sfx_s8 lbt_thr_off)
{
  st_manuf_context->lbt_thr_offset=lbt_thr_off;

  return SFX_ERR_NONE;
}

sfx_u8 ST_RF_API_get_lbt_thr_offset(sfx_s8 *lbt_thr_off)
{
  (*lbt_thr_off)=st_manuf_context->lbt_thr_offset;

  return SFX_ERR_NONE;
}

sfx_u8 ST_RF_API_reduce_output_power(int16_t reduction)
{
//  if((int16_t)st_manuf_context->bpsk_ramps->fifo_ramp_fast[3]+reduction<st_manuf_context->ramps_settings->max_power)
//  {}//return ST_MANUF_POWER_ERROR;

  st_manuf_context->power_reduction=reduction;

  return SFX_ERR_NONE;
}

sfx_u8 ST_RF_API_set_tcxo(sfx_u8 tcxo)
{
  st_manuf_context->tcxo_flag=tcxo;

  return SFX_ERR_NONE;
}

sfx_u8 ST_RF_API_set_pa(sfx_u8 pa)
{
  st_manuf_context->pa_flag=pa;

  return SFX_ERR_NONE;
}

sfx_u8 ST_RF_API_get_ramp_duration(void)
{
  return st_manuf_context->ramps_settings.ramp_start_duration;
}

sfx_u8 ST_RF_API_smps(uint8_t mode)
{
  st_manuf_context->smps_mode=mode;

  return SFX_ERR_NONE;
}

sfx_u8 ST_RF_API_Get_Continuous_TX_or_MONARCH_Scan_Flag(void)
{
  return (sfx_u8) st_manuf_context->tx_packet_struct.continuous_tx_monarch_flag;
}

sfx_u8 ST_RF_API_StartTx(void)
{
  /*Configure External FE module*/
  if (st_manuf_context->pa_flag == 0)
    FEM_Operation(FEM_TX_BYPASS);
  else
    FEM_Operation(FEM_TX);

  /*Put S2LP in TX*/
  CMD_STROBE_TX();
  return SFX_ERR_NONE;
}

sfx_u8 ST_RF_API_StartRx(void)
{
  /*Configure External FE module in RX*/
  FEM_Operation(FEM_RX);
  /*Put S2LP in RX*/
  CMD_STROBE_RX();
  return SFX_ERR_NONE;
}

sfx_u8 ST_RF_API_StopRxTx(void)
{
  /*Put S2LP in READY*/
  CMD_STROBE_SABORT();

  /*Configure External FE module in RX*/
  FEM_Operation(FEM_SHUTDOWN);

  return SFX_ERR_NONE;
}

sfx_s16 ST_RF_API_GetRSSI(void)
{
  sfx_u8  last_rssi;
  /* Read the RSSI value captured at the end of the SYNC word detection of the received packet */
  priv_ST_MANUF_ReadRegisters(0xA2, 1, &last_rssi); //RSSI_REG
  return (sfx_s16) (last_rssi-146+st_manuf_context->rssi_offset-6);
}

/* Retrieve FIFO data */
void ST_RF_API_ReadFifo(sfx_u8 n_bytes, sfx_u8* buffer, sfx_u8 flush )
{
  /* Read the num of bytes stored into the RX FIFO */
  priv_ST_MANUF_ReadFifo(n_bytes, buffer);

  if (flush)
    CMD_STROBE_FRX();
}

/* Retrieve FIFO data */
sfx_u8 ST_RF_API_ReadFifoBytes()
{
  /* Read the num of bytes stored into the RX FIFO */
  sfx_u8 occuped_slot;
  priv_ST_MANUF_ReadRegisters(0x90, 1, &occuped_slot);

  return occuped_slot;
}

void ST_RF_API_SetFifoLength(sfx_u8 n_bytes)
{
  // Set the almost full threshold (It starts form the top of the fifo)
  sfx_u8 reg=128-n_bytes;

  priv_ST_MANUF_WriteRegisters(0x3C,1, &reg); //FIFO_CONFIG3

  CMD_STROBE_FRX(); /*Flush fifo after threshold setting*/
}

/* Monarch weak functions */

__weak sfx_u8 MONARCH_API_malloc(sfx_u16 size, sfx_u8 **returned_pointer) { return MONARCH_ERR_API_MALLOC; }

__weak sfx_u8 MONARCH_API_free(sfx_u8 *ptr) { return MONARCH_ERR_API_FREE; }

__weak sfx_u8 MONARCH_API_timer_start (sfx_u16 timer_value, sfx_timer_unit_enum_t unit, sfx_error_t(* timeout_callback_handler)(void)) { return MONARCH_ERR_API_TIMER_START; }

__weak sfx_u8 MONARCH_API_timer_stop (void) { return SFX_ERR_API_GET_VERSION; }

__weak sfx_u8 MONARCH_API_configure_search_pattern ( sfx_monarch_pattern_search_t list_freq_pattern[],
								    sfx_u8 size,
								    sfx_monarch_listening_mode_t mode,
								    sfx_error_t(* monarch_pattern_freq_result_callback_handler)(sfx_u32 freq, sfx_pattern_enum_t pattern, sfx_s16 rssi)){ return MONARCH_ERR_API_CONFIGURE_SEARCH_PATTERN; }

__weak sfx_u8 MONARCH_API_stop_search_pattern(void) { return MONARCH_ERR_API_STOP_SEARCH_PATTERN; }

__weak sfx_u8 MONARCH_API_get_version(sfx_u8 **version, sfx_u8 *size) { return MONARCH_ERR_API_TIMER_STOP; }
