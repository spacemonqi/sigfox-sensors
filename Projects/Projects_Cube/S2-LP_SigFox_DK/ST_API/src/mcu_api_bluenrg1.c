#include <stdint.h>
#include <stdio.h>
#include "sigfox_stack.h"
#include "SDK_EVAL_Config.h"
#include "BlueNRG1_conf.h"
#include "clock.h"
#include "SDK_UTILS_Timers.h"

#include "S2LP_Middleware_Config.h"

#ifdef MONARCH_FEATURE_ENABLED
	#include "st_monarch_api.h"
#endif

//Board-Chip dependent
#include "BlueNRG1_mft.h"
#include "BlueNRG_x_device.h"

#ifdef DEBUG
	#include <stdio.h>
	void ST_dbg_CB(const char *vectcStr,...);
	#define PRINTF(...)     { ST_dbg_CB(__VA_ARGS__);}
#elif DEBUG_BLE
	#include <stdio.h>
	#include "SDK_EVAL_Com.h"
	#define PRINTF(...) printf(__VA_ARGS__)
#else
	#define PRINTF(...)
#endif

//Implemented in main
void ST_MANUF_report_CB(uint8_t status, int32_t rssi);

/* The following define instructs this driver to save the data inside the flash of the BlueNRG-1.
*  If undefined, the sigfox NVM data will be written into the external EEPROM of the board. */
// #define NVM_IN_MCU

/*!
 * \defgroup MCU_ERR_API_xx codes Return Error codes definition for MCU API
 *
 * \brief Can be customized to add new error codes.
 * All MCU_API_ error codes will be piped with SIGFOX_API_xxx return code.<BR>
 *
 * IMPORTANT : SFX_ERR_NONE return code is mandatory when no error for each MCU_API_xxx RF_API_xxx REPEATER_API_xxx or SE_API_xxx
 * functions.
 *
 *  @{
 */

/* ---------------------------------------------------------------- */
/* Bytes reserved for MCU API ERROR CODES : From 0x10 to 0x2F       */
/* ---------------------------------------------------------------- */

#define MCU_ERR_API_MALLOC                  (sfx_u8)(0x11) /*!< Error on MCU_API_malloc */
#define MCU_ERR_API_FREE                    (sfx_u8)(0x12) /*!< Error on MCU_API_free */
#define MCU_ERR_API_VOLT_TEMP               (sfx_u8)(0x13) /*!< Error on MCU_API_get_voltage_temperature */
#define MCU_ERR_API_DLY                     (sfx_u8)(0x14) /*!< Error on MCU_API_delay */
#define MCU_ERR_API_AES                     (sfx_u8)(0x15) /*!< Error on MCU_API_aes_128_cbc_encrypt */
#define MCU_ERR_API_GETNVMEM                (sfx_u8)(0x16) /*!< Error on MCU_API_get_nv_mem */
#define MCU_ERR_API_SETNVMEM                (sfx_u8)(0x17) /*!< Error on MCU_API_set_nv_mem */
#define MCU_ERR_API_TIMER_START             (sfx_u8)(0x18) /*!< Error on MCU_API_timer_start */
#define MCU_ERR_API_TIMER_START_CS          (sfx_u8)(0x19) /*!< Error on MCU_API_timer_start_carrier_sense */
#define MCU_ERR_API_TIMER_STOP_CS           (sfx_u8)(0x1A) /*!< Error on MCU_API_timer_stop_carrier_sense */
#define MCU_ERR_API_TIMER_STOP              (sfx_u8)(0x1B) /*!< Error on MCU_API_timer_stop */
#define MCU_ERR_API_TIMER_END               (sfx_u8)(0x1C) /*!< Error on MCU_API_timer_wait_for_end */
#define MCU_ERR_API_TEST_REPORT             (sfx_u8)(0x1D) /*!< Error on MCU_API_report_test_result */
#define MCU_ERR_API_GET_VERSION             (sfx_u8)(0x1E) /*!< Error on MCU_API_get_version */

#if defined CREDENTIALS_SECURE_ELEMENT || defined CREDENTIALS_UNCRYPTED
 #define MCU_ERR_API_GET_ID                  (sfx_u8)(0x1F) /*!< Error on MCU_API_get_device_id */
 #define MCU_ERR_API_GET_PAC                 (sfx_u8)(0x20) /*!< Error on MCU_API_get_initial_pac */
#else
 #define MCU_ERR_API_AES_GET_CRYPT           (sfx_u8)(0x21) /*!< Error on MCU_API_get_encrypted_info */
 #define MCU_ERR_API_AES_DECRYPT             (sfx_u8)(0x22) /*!< Error on MCU_API_aes_128_cbc_decrypt */
#endif

/* ---------------------------------------------------------------- */
/* Bytes reserved for RF API ERROR CODES : From 0x30 to 0x3F        */
/* ---------------------------------------------------------------- */

/* ---------------------------------------------------------------- */
/* Bytes reserved for SE API ERROR CODES : From 0x40 to 0x5F        */
/* ---------------------------------------------------------------- */

/* ---------------------------------------------------------------- */
/* Bytes reserved for REPEATER API ERROR CODES : From 0x60 to 0x7F  */
/* ---------------------------------------------------------------- */

#define ST_TRUE  1
#define ST_FALSE 0

#if defined(USE_STM32L0XX_NUCLEO) || defined(USE_STM32F0XX_NUCLEO)
#define IRQ_PRIORITY 0x00
#else
#define IRQ_PRIORITY 0x0A
#endif

#define MCU_API_VER		"v2.4.5"
static const uint8_t _libVersion[] = MCU_API_VER;

/** @}*/
volatile uint8_t rtc_irq=0, rtc_in_use=0, rtc_in_use_for_cs=0, carrier_sense_tim_started=0;
static   uint8_t _encryptedPayload = 0;

//To manage MFT overflow in carrier sense
uint8_t  mft_reload_cnt=0; // Number of current interrupt cycle
uint16_t n_int_cycle=0;    // Number if interruots to be executed for a timeout session
uint16_t residual=0;       // Rest of integer division, to be programmed

//Local Functions
void priv_MFT_Configuration(void);

void ST_dbg_CB(const char *vectcStr,...){}

void ST_MANUF_report_CB(uint8_t status, int32_t rssi)
{
#ifndef MONARCH_CLI_TESTS
  if(status)
    printf("{TEST PASSED! RSSI=%d}\r\n",rssi);
  else
    printf("{TEST FAILED!}\r\n");

  //SdkDelayMs(300); uncomment this line for monarch verified add-on tests #7 and #8
#endif
}

void RTC_Handler(void)
{
  if(SET == RTC_IT_Status(RTC_IT_TIMER))
  {
    /* Clear pending interrupt flag */
    RTC_IT_Clear(RTC_IT_TIMER);

    rtc_in_use=0;
    rtc_irq=1;
    if(rtc_in_use_for_cs)
    {
	rtc_in_use_for_cs=0;
	ST_RF_API_Timer_Channel_Clear_CB();
    }
    else
    {
	ST_RF_API_Timer_CB(TIMER_STOP);
    }
  }
}

void MFT1B_Handler(void)
{
  if (MFT_StatusIT(MFT1,MFT_IT_TND) != RESET)
  {
    if (n_int_cycle==0 || (mft_reload_cnt==n_int_cycle+1)) // Only in the residual part the callbacl will be called
	ST_RF_API_Timer_Channel_Clear_CB();

    else if (mft_reload_cnt==n_int_cycle) //Load the residual part and increment counter
    {
	MFT_Cmd(MFT1, DISABLE);
	MFT_SetCounter2(MFT1, residual);
	MFT_Cmd(MFT1, ENABLE);
	mft_reload_cnt++;
    }
    else
	mft_reload_cnt++; //Increment counter

    MFT_ClearIT(MFT1, MFT_IT_TND);
  }
}

void S2LPSpiRawTc(void)
{
  S2LPSetSpiInUse(0);
}

void USER_DMA_SPI_RX_Callback(void)
{
  /* DMA_CH disable */
  DMA_CH_SPI_TX->CCR_b.EN = RESET;
  DMA_CH_SPI_RX->CCR_b.EN = RESET;

  while (SET == SPI_GetFlagStatus(SPI_FLAG_BSY));

  GPIO_SetBits(S2LP_SPI_CS_PIN);

  SPI_Cmd(DISABLE);

  NVIC_Init(&(NVIC_InitType){DMA_IRQn,MED_PRIORITY,DISABLE});

  //DMA_ClearFlag(DMA_CH_SPI_TX_IT_TC);

  S2LPSpiRawTc();
}

void handleS2LPIRQ(void){
  /* Avoid to refill the FIFO wile is still filling */
  if (ST_RF_API_GetFIFOState()==ST_FIFO_STATE_WAITING_UNDERFLOW)
  {
    ST_RF_API_S2LP_IRQ_CB();
  }
}

void ST_MCU_API_WaitForInterrupt(void)
{
  /* If the MCU is stuck waiting for some IRQ */
  /* you can, for example, call the BLE_Activity() function here */
}

static void priv_ST_MCU_API_delay(uint32_t delay_ms)
{
  /* Get the initial timestamp */
  uint32_t t0 = SdkGetCurrentSysTick();

  /* wait the delay_ms amount of time */
  while(SdkGetCurrentSysTick()-t0<delay_ms)
  {
    /* call the ST_MCU_API_WaitForInterrupt fcn  */
    ST_MCU_API_WaitForInterrupt();
  }
}

/*!******************************************************************
 * \fn sfx_u8 MCU_API_malloc(sfx_u16 size, sfx_u8 **returned_pointer)
 * \brief Allocate memory for library usage (Memory usage = size (Bytes))
 * This function is only called once at the opening of the Sigfox Library ( SIGF
 *
 * IMPORTANT NOTE:
 * --------------
 * The address reported need to be aligned with architecture of the microprocessor used.
 * For a Microprocessor of:
 *   - 8 bits  => any address is allowed
 *   - 16 bits => only address multiple of 2 are allowed
 *   - 32 bits => only address multiple of 4 are allowed
 *
 * \param[in] sfx_u16 size                  size of buffer to allocate in bytes
 * \param[out] sfx_u8 **returned_pointer    pointer to buffer (can be static)
 *
 * \retval SFX_ERR_MANUF_NONE:              No error
 * \retval SFX_ERR_MANUF_MALLOC:            Malloc error
 *
 * \xxx   Function skeleton example
  -------------------------
   {
     - Allocate a buffer of size 'size'
     - Returns the pointer on this memory area
   }

 *******************************************************************/
sfx_u8 MCU_API_malloc(sfx_u16 size, sfx_u8 **returned_pointer)
{
  PRINTF("MCU_API_malloc IN\n\r");

  // Allocate a memory : static or dynamic allocation
  // knowing that the sigfox library will ask for a buffer once at the SIGFOX_API_open() call.
  // this buffer will be release after SIGFOX_API_close() call.
  static sfx_u32 mem[500/4];

  if(size>500)
  {
    PRINTF("MCU_API_malloc OUT\n\r");
    return MCU_ERR_API_MALLOC;
  }
  else
  {
    (*returned_pointer)=(sfx_u8*)mem;
  }

  PRINTF("MCU_API_malloc OUT\n\r");

  return SFX_ERR_NONE;
}

/*!******************************************************************
 * \fn sfx_u8 MCU_API_free(sfx_u8 *ptr)
 * \brief Free memory allocated to library
 *
 * \param[in] sfx_u8 *ptr                   pointer to buffer
 * \param[out] none
 *
 * \retval SFX_ERR_NONE:                    No error
 * \retval MCU_ERR_API_FREE:                Free error
 *******************************************************************/
sfx_u8 MCU_API_free(sfx_u8 *ptr)
{
  // Free the buffer allocated during the MCU_API_malloc()
  // called only when SIGFOX_API_close() is called.
  PRINTF("MCU_API_free IN\n\r");
  PRINTF("MCU_API_free OUT\n\r");
  return SFX_ERR_NONE;
}

/*!******************************************************************
 * \fn sfx_u8 MCU_API_get_voltage_temperature(sfx_u16 *voltage_idle, sfx_u16 *voltage_tx, sfx_u16 *temperature)
 * \brief Get voltage and temperature for Out of band frames
 * Value must respect the units bellow for <B>backend compatibility</B>
 *
 * \param[in] none
 * \param[out] sfx_u16 *voltage_idle        Device's voltage in Idle state (mV)
 * \param[out] sfx_u16 *voltage_tx          Device's voltage in Tx state (mV) - for the last transmission
 * \param[out] sfx_u16 *temperature         Device's temperature in 1/10 of degrees celcius
 *
 * \retval SFX_ERR_NONE:                    No error
 * \retval MCU_ERR_API_VOLT_TEMP:           Get voltage/temperature error
 *******************************************************************/
sfx_u8 MCU_API_get_voltage_temperature(sfx_u16 *voltage_idle,
						   sfx_u16 *voltage_tx,
						   sfx_s16 *temperature)
{
  PRINTF("MCU_API_get_voltage_temperature IN\n\r");

  /* Get the idle voltage of the complete device
  *  get the temperature of the device
  *  if those values are not available : set it to 0x0000
  *  return the voltage_idle in 1/10 volt on 16bits and 1/10 degrees for the temperature */
  (*voltage_idle)=0;
  (*voltage_tx)=0;
  (*temperature)=0;

  PRINTF("MCU_API_get_voltage_temperature OUT\n\r");

  return SFX_ERR_NONE;
}


/*!******************************************************************
 * \fn sfx_u8 MCU_API_delay(sfx_delay_t delay_type)
 * \brief Inter stream delay, called between each RF_API_send
 * - SFX_DLY_INTER_FRAME_TX  : 0 to 2s in Uplink DC
 * - SFX_DLY_INTER_FRAME_TRX : 500 ms in Uplink/Downlink FH & Downlink DC
 * - SFX_DLY_OOB_ACK :         1.4s to 4s for Downlink OOB
 * - SFX_DLY_SENSI :           4s for sensitivity test mode
 * - SFX_CS_SLEEP :            delay between several trials of Carrier Sense (for the first frame only)
 *
 * \param[in] sfx_delay_t delay_type        Type of delay to call
 * \param[out] none
 *
 * \retval SFX_ERR_NONE:                  No error
 * \retval MCU_ERR_API_DLY:               Delay error
 *******************************************************************/
sfx_u8 MCU_API_delay(sfx_delay_t delay_type)
{
  PRINTF("MCU_API_delay IN (%d)\n\r",delay_type);

  switch(delay_type)
  {
  case SFX_DLY_INTER_FRAME_TRX:
    //Adjust timing offset if needed
    //priv_ST_MCU_API_delay(500-custom_offset*ST_RF_API_get_ramp_duration());
    //break;
  case SFX_DLY_INTER_FRAME_TX:
  case SFX_DLY_CS_SLEEP:
    /* Ramping should be considered in the ramp up/down:
    * since we have 72 samples in the ramp
    * (18ms for each ramp, we need to compensate 36 ms)
    * Moreover we have also 6ms of silence (2 before and 4 after packet) */
    priv_ST_MCU_API_delay(500-2*ST_RF_API_get_ramp_duration());
    break;
  case SFX_DLY_OOB_ACK:
    priv_ST_MCU_API_delay(2000-2*ST_RF_API_get_ramp_duration());
    break;
  }

  PRINTF("MCU_API_delay OUT\n\r");

  return SFX_ERR_NONE;
}
/*!******************************************************************
 * \fn sfx_u8 MCU_API_aes_128_cbc_encrypt(sfx_u8 *encrypted_data, sfx_u8 *data_to_encrypt, sfx_u8 aes_block_len, sfx_u8 key[16], sfx_credentials_use_key_t use_key)
 * \brief Encrypt a complete buffer with Secret or Test key.<BR>
 * The secret key corresponds to the private key provided from the CRA.
 * <B>These keys must be stored in a secure place.</B> <BR>
 * Can be hardcoded or soft coded (iv vector contains '0')
 *
 * \param[out] sfx_u8 *encrypted_data            Result of AES Encryption
 * \param[in] sfx_u8 *data_to_encrypt            Input data to Encrypt
 * \param[in] sfx_u8 aes_block_len               Input data length (should be a multiple of an AES block size, ie. AES_BLOCK_SIZE bytes)
 * \param[in] sfx_u8 key[16]                     Input key
 * \param[in] sfx_credentials_use_key_t use_key  Key to use - private key or input key
 *
 * \retval SFX_ERR_NONE:                         No error
 * \retval MCU_ERR_API_AES:                      AES Encryption error
 *******************************************************************/
sfx_u8 MCU_API_aes_128_cbc_encrypt(sfx_u8 *encrypted_data,
                                   sfx_u8 *data_to_encrypt,
                                   sfx_u8 aes_block_len,
                                   sfx_u8 key[16],
                                   sfx_credentials_use_key_t use_key)
{
  /*  Let the retriever encrypts the requested buffer using the ID_KEY_RETRIEVER function.
   *  The retriever knows the KEY of this node. */
  PRINTF("MCU_API_aes_128_cbc_encrypt IN\n\r");
  enc_utils_encrypt(encrypted_data,data_to_encrypt,aes_block_len,key,use_key);
  PRINTF("MCU_API_aes_128_cbc_encrypt OUT\n\r");

  return SFX_ERR_NONE;
}

/*!******************************************************************
 * \fn sfx_u8 MCU_API_get_nv_mem(sfx_u8 *read_data)
 * \brief Get data from non volatile memory.<BR>
 * The size of the data to read is \link SFX_NVMEM_BLOCK_SIZE \endlink
 * bytes.
 * CAREFUL : this value can change according to the features included
 * in the library (covered zones, etc.)
 *
 * \param[in] none
 * \param[out] sfx_u8 read_data[SFX_NVMEM_BLOCK_SIZE] Pointer to the data bloc to write with the data stored in memory
 *
 * \retval SFX_ERR_NONE:                  No error
 * \retval MCU_ERR_API_GETNVMEM:          Read nvmem error
 *******************************************************************/
sfx_u8 MCU_API_get_nv_mem(sfx_u8 read_data[SFX_NVMEM_BLOCK_SIZE])
{
  PRINTF("MCU_API_get_nv_mem IN\n\r");

  /* Read data */
  NVM_RW_RESULTS res = NVM_ReadRecord((uint8_t *)read_data, SFX_NVMEM_BLOCK_SIZE);

  PRINTF("MCU_API_get_nv_mem OUT\n\r");
  return res;
}

/*!******************************************************************
 * \fn sfx_u8 MCU_API_set_nv_mem(sfx_u8 *data_to_write)
 * \brief Set data to non volatile memory.<BR> It is strongly
 * recommanded to use NV memory like EEPROM since this function
 * is called at each SIGFOX_API_send_xxx.
 * The size of the data to write is \link SFX_NVMEM_BLOCK_SIZE \endlink
 * bytes.
 * CAREFUL : this value can change according to the features included
 * in the library (covered zones, etc.)
 *
 * \param[in] sfx_u8 data_to_write[SFX_NVMEM_BLOCK_SIZE] Pointer to data bloc to be written in memory
 * \param[out] none
 *
 * \retval SFX_ERR_NONE:              No error
 * \retval MCU_ERR_API_SETNVMEM:      Write nvmem error
 *******************************************************************/
sfx_u8 MCU_API_set_nv_mem(sfx_u8 data_to_write[SFX_NVMEM_BLOCK_SIZE])
{
  PRINTF("MCU_API_set_nv_mem IN\n\r");

  /* Write data */
  NVM_RW_RESULTS res = NVM_WriteRecord((uint8_t *)data_to_write, SFX_NVMEM_BLOCK_SIZE);

  PRINTF("MCU_API_set_nv_mem OUT\n\r");
  return res;
}

/*!******************************************************************
 * \fn sfx_u8 MCU_API_timer_start_carrier_sense(sfx_u16 time_duration_in_ms)
 * \brief Start timer for :
 * - carrier sense maximum window (used in ARIB standard)
 *
 * \param[in] sfx_u16 time_duration_in_ms    Timer value in milliseconds
 * \param[out] none
 *
 * \retval SFX_ERR_NONE:                  No error
 * \retval MCU_ERR_API_TIMER_START_CS:    Start CS timer error
 *******************************************************************/
sfx_u8 MCU_API_timer_start_carrier_sense(sfx_u16 time_duration_in_ms)
{
  PRINTF("MCU_API_timer_start_carrier_sense for %d msIN\n\r", time_duration_in_ms);

  carrier_sense_tim_started=1;

  if(rtc_in_use)
  {
    PRINTF("\t \t \t CARRIER SENSE W/O RTC. %d\n\r", time_duration_in_ms);
    NVIC_InitType NVIC_InitStructure;
    MFT_InitType timer_init;

    SysCtrl_PeripheralClockCmd(CLOCK_PERIPH_MTFX1, ENABLE);
    MFT_StructInit(&timer_init);

    timer_init.MFT_Mode = MFT_MODE_1;
    timer_init.MFT_Prescaler = 160-1;	/* 10 us clock for 16MHz 5 us for 32 MHz */
    /* MFT1 configuration */
    timer_init.MFT_Clock2 = MFT_PRESCALED_CLK;
    MFT_Init(MFT1, &timer_init);

    /* Managing counter overflow*/
    mft_reload_cnt=0;
#if (HS_SPEED_XTAL == HS_SPEED_XTAL_32MHZ)
    uint32_t n_tick = ((uint32_t)time_duration_in_ms*200); //Number of tick for 5 us tick (32MHz)
    n_int_cycle = n_tick/SFX_U16_MAX;
    residual = n_tick % SFX_U16_MAX;
    PRINTF ("\t\t\t\t\tNO CYCLES: %d, RESIDUAL: %d ", n_int_cycle,residual);
#else
    uint32_t n_tick = ((uint32_t)time_duration_in_ms*100); //Number of tick for 10 us tick (16MHz)
    n_int_cycle = n_tick/SFX_U16_MAX;
    residual = n_tick % SFX_U16_MAX;
    PRINTF ("\t\t\t\t\tNO CYCLES: %d, RESIDUAL: %d ", n_int_cycle,residual);
#endif

    if (n_int_cycle==0)
	MFT_SetCounter2(MFT1, residual); /* If it's enough 16 bit, only the rest of the division is assigned */
    else
	MFT_SetCounter2(MFT1, SFX_U16_MAX); /* If it's NOT enough 16 bit, the first cycle is at the MAX */
    /* End Managing counter overflow*/

    /* Enable MFT2 Interrupt 1 */
    NVIC_InitStructure.NVIC_IRQChannel = MFT1B_IRQn;
    NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = LOW_PRIORITY;
    NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE;
    NVIC_Init(&NVIC_InitStructure);

    /* Enable the MFT interrupt */
    MFT_EnableIT(MFT1, MFT_IT_TND, ENABLE);

    MFT_Cmd(MFT1, ENABLE);
  }
  else
  {
    PRINTF("\t \t \t CARRIER SENSE WITH RTC!!! %d\n\r", time_duration_in_ms);
    RTC_InitType RTC_Init_struct;
    NVIC_InitType NVIC_InitStructure;

    SysCtrl_PeripheralClockCmd(CLOCK_PERIPH_RTC, ENABLE);

    /* RTC configuration */
    RTC_Init_struct.RTC_operatingMode = RTC_TIMER_ONESHOT;     /**< Periodic RTC mode */
    RTC_Init_struct.RTC_PATTERN_SIZE = 0;                       /**< Pattern size set to 0 */
    RTC_Init_struct.RTC_TLR1 = time_duration_in_ms*33;             /**< Enable 1s timer period */
    RTC_Init_struct.RTC_TLR2 = 0;                               /**< Enable 1s timer period */
    RTC_Init_struct.RTC_PATTERN1 = 0x00;                        /**< RTC_TLR1 selected for time generation */
    RTC_Init_struct.RTC_PATTERN2 = 0x00;                        /**< RTC_TLR1 selected for time generation */
    RTC_Init_struct.RTC_PATTERN3 = 0x00;                        /**< RTC_TLR1 selected for time generation */
    RTC_Init_struct.RTC_PATTERN4 = 0x00;                        /**< RTC_TLR1 selected for time generation */
    RTC_Init(&RTC_Init_struct);

    /* Enable RTC Timer interrupt*/
    RTC_IT_Config(RTC_IT_TIMER, ENABLE);
    RTC_IT_Clear(RTC_IT_TIMER);

    /** Delay between two write in RTC->TCR register has to be
    *  at least 3 x 32k cycle + 2 CPU cycle. For that reason it
    *  is neccessary to add the delay.
    */
    for (volatile uint32_t i=0; i<600; i++) {
	__asm("NOP");
    }

    /* Set the RTC_IRQn interrupt priority and enable it */
    NVIC_InitStructure.NVIC_IRQChannel = RTC_IRQn;
    NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = LOW_PRIORITY;
    NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE;
    NVIC_Init(&NVIC_InitStructure);

    rtc_in_use=1;
    rtc_in_use_for_cs=1;
    rtc_irq=0;


    /* Enable RTC */
    RTC_Cmd(ENABLE);
  }

  PRINTF("MCU_API_timer_start_carrier_sense OUT\n\r");
  return SFX_ERR_NONE;
}

/*!******************************************************************
 * \fn sfx_u8 MCU_API_timer_start(sfx_u16 time_duration_in_s)
 * \brief Start timer for :
 * - 20 seconds wait in downlink
 * - 25 seconds listening in downlink
 * - 6 seconds listening in sensitivity test mode
 * - 0 to 255 seconds listening in GFSK test mode (config argument)
 *
 * \param[in] sfx_u16 time_duration_in_s    Timer value in seconds
 * \param[out] none
 *
 * \retval SFX_ERR_NONE:                  No error
 * \retval MCU_ERR_API_TIMER_START:       Start timer error
 *******************************************************************/
sfx_u8 MCU_API_timer_start(sfx_u32 time_duration_in_s)
{
  PRINTF("MCU_API_timer_start IN , duration(s): %d\n\r", time_duration_in_s);
  ST_RF_API_Timer_CB(TIMER_START);
  //Stop any previous session if present
  RTC_Cmd(DISABLE);

  //If previously has not been disbled, reset it
  RTC_InitType RTC_Init_struct;
  NVIC_InitType NVIC_InitStructure;

  SysCtrl_PeripheralClockCmd(CLOCK_PERIPH_RTC, ENABLE);
  /* RTC configuration */
  RTC_Init_struct.RTC_operatingMode = RTC_TIMER_ONESHOT;                /**< Periodic RTC mode */
  RTC_Init_struct.RTC_PATTERN_SIZE = 1 - 1;                             /**< Pattern size set to 0 */
  RTC_Init_struct.RTC_TLR1 = (uint32_t)time_duration_in_s*32767;        /**< Enable 1s timer period */
  RTC_Init_struct.RTC_TLR2 = 0;                               /**< Enable 1s timer period */
  RTC_Init_struct.RTC_PATTERN1 = 0x00;                        /**< RTC_TLR1 selected for time generation */
  RTC_Init_struct.RTC_PATTERN2 = 0x00;                        /**< RTC_TLR1 selected for time generation */
  RTC_Init_struct.RTC_PATTERN3 = 0x00;                        /**< RTC_TLR1 selected for time generation */
  RTC_Init_struct.RTC_PATTERN4 = 0x00;                        /**< RTC_TLR1 selected for time generation */
  RTC_Init(&RTC_Init_struct);

  /* Enable RTC Timer interrupt*/
  RTC_IT_Config(RTC_IT_TIMER, ENABLE);
  RTC_IT_Clear(RTC_IT_TIMER);

  /** Delay between two write in RTC->TCR register has to be
  *  at least 3 x 32k cycle + 2 CPU cycle. For that reason it
  *  is neccessary to add the delay.
  */
  for (volatile uint32_t i=0; i<600; i++) {
    __asm("NOP");
  }

  /* Set the RTC_IRQn interrupt priority and enable it */
  NVIC_InitStructure.NVIC_IRQChannel = RTC_IRQn;
  NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = LOW_PRIORITY;
  NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE;
  NVIC_Init(&NVIC_InitStructure);

  rtc_in_use=1;
  rtc_irq=0;
  /* Enable RTC */
  RTC_Cmd(ENABLE);
  PRINTF("MCU_API_timer_start OUT\n\r");
  return SFX_ERR_NONE;
}

/*!******************************************************************
 * \fn sfx_u8 MCU_API_timer_stop(void)
 * \brief Stop the timer (started with MCU_API_timer_start)
 *
 * \param[in] none
 * \param[out] none
 *
 * \retval SFX_ERR_NONE:                    No error
 * \retval MCU_ERR_API_TIMER_STOP:          Stop timer error
 *******************************************************************/
sfx_u8 MCU_API_timer_stop(void)
{
  PRINTF("MCU_API_timer_stop IN\n\r");
  RTC_Cmd(DISABLE);
  rtc_in_use=0;
  PRINTF("MCU_API_timer_stop OUT\n\r");
  return SFX_ERR_NONE;
}

/*!******************************************************************
 * \fn sfx_u8 MCU_API_timer_stop_carrier_sense(void)
 * \brief Stop the timer (started with MCU_API_timer_start_carrier_sense)
 *
 * \param[in] none
 * \param[out] none
 *
 * \retval SFX_ERR_NONE:                  No error
 * \retval MCU_ERR_API_TIMER_STOP_CS:     Stop timer error
 *******************************************************************/
sfx_u8 MCU_API_timer_stop_carrier_sense(void)
{
  PRINTF("MCU_API_timer_stop_carrier_sense IN\n\r");

  if(rtc_in_use_for_cs)
  {
    RTC_Cmd(DISABLE);
    rtc_in_use=0;
    rtc_in_use_for_cs=0;
  }
  else
  {
    MFT_EnableIT(MFT1, MFT_IT_TND, DISABLE);
    MFT_Cmd(MFT1, DISABLE);
  }
  carrier_sense_tim_started=0;



  PRINTF("MCU_API_timer_stop_carrier_sense OUT\n\r");

  return SFX_ERR_NONE;
}

/*!******************************************************************
 * \fn sfx_u8 MCU_API_timer_wait_for_end(void)
 * \brief Blocking function to wait for interrupt indicating timer
 * elapsed.<BR> This function is only used for the 20 seconds wait
 * in downlink.
 *
 * \param[in] none
 * \param[out] none
 *
 * \retval SFX_ERR_NONE:                  No error
 * \retval MCU_ERR_API_TIMER_END:         Wait end of timer error
 *******************************************************************/
sfx_u8 MCU_API_timer_wait_for_end(void)
{
  PRINTF("MCU_API_timer_wait_for_end IN\n\r");

  while(!rtc_irq)
  {
    ST_MCU_API_WaitForInterrupt();
  }
  rtc_irq=0;

  PRINTF("MCU_API_timer_wait_for_end OUT\n\r");
  return SFX_ERR_NONE;
}

/*!******************************************************************
 * \fn sfx_u8 MCU_API_report_test_result(sfx_bool status, sfx_s16 rssi)
 * \brief To report the result of Rx test for each valid message
 * received/validated by library.<BR> Manufacturer api to show the result
 * of RX test mode : can be uplink radio frame or uart print or
 * gpio output.
 * RSSI parameter is only used to report the rssi of received frames (downlink test)
 *
 * \param[in] sfx_bool status               Is SFX_TRUE when result ok else SFX_FALSE
 *                                          See SIGFOX_API_test_mode summary
 * \param[out] rssi                         RSSI of the received frame
 *
 * \retval SFX_ERR_NONE:                    No error
 * \retval MCU_ERR_API_TEST_REPORT:         Report test result error
 *******************************************************************/
sfx_u8 MCU_API_report_test_result(sfx_bool status, sfx_s16 rssi)
{
  ST_MANUF_report_CB(status, rssi);

  // Use this function to : print output result : status and rssi on uart if you have one or any link is available on device
  // or use a gpio to indicate at least the status
  // or to send a message over the air using any link to report the status with rssi
  // you could also use the RF part in specific modulation (ook ask or gfsk or else to return status and rssi
  return SFX_ERR_NONE;
}

/*!******************************************************************
 * \fn sfx_u8 MCU_API_get_version(sfx_u8 **version, sfx_u8 *size)
 * \brief Returns current MCU API version
 *
 * \param[out] sfx_u8 **version                 Pointer to Byte array (ASCII format) containing library version
 * \param[out] sfx_u8 *size                     Size of the byte array pointed by *version
 *
 * \retval SFX_ERR_NONE:                No error
 * \retval MCU_ERR_API_GET_VERSION:     Get Version error
 *******************************************************************/
sfx_u8 MCU_API_get_version(sfx_u8 **version, sfx_u8 *size)
{
  (*size) = sizeof(_libVersion);
  (*version) = (sfx_u8*)_libVersion;

  return SFX_ERR_NONE;
}

sfx_u8 MCU_API_get_device_id_and_payload_encryption_flag(sfx_u8 dev_id[ID_LENGTH], sfx_bool *payload_encryption_enabled)
{
  PRINTF("MCU_API_get_device_id_and_payload_encryption_flag IN\n\r");
  enc_utils_get_id(dev_id);
  (*payload_encryption_enabled)=_encryptedPayload;
  PRINTF("MCU_API_get_device_id_and_payload_encryption_flag OUT\n\r");

  return SFX_ERR_NONE;
}

sfx_u8 MCU_API_get_initial_pac(sfx_u8 initial_pac[PAC_LENGTH])
{
  PRINTF("MCU_API_get_initial_pac IN\n\r");
  enc_utils_get_initial_pac(initial_pac);
  PRINTF("MCU_API_get_initial_pac OUT\n\r");

  return SFX_ERR_NONE;
}

void ST_MCU_API_SetEncryptionPayload(uint8_t ePayload)
{
  _encryptedPayload = ePayload;
}

/* trigger 1: rising, 0: falling*/
void ST_MCU_API_GpioIRQ(sfx_u8 new_state, sfx_u8 trigger)
{
  /* Configure the MCU IRQ connected to the specified S2-LP GPIO */
  /* trigger 1: rising, 0: falling (default) */
  S2LPIRQInit();
  S2LPIRQEnable(new_state, trigger);
}

void ST_MCU_API_Shutdown(sfx_u8 value)
{
  if(value)
  {
    S2LPShutdownEnter();
    TCXO_Operation(TCXO_OFF);
  }
  else
  {
    TCXO_Init();
    TCXO_Operation(TCXO_ON);
    S2LPShutdownExit();
  }

  /* wait 3 ms to wait the device to be ready */
  SdkDelayMs(3);
}

void ST_MCU_API_SpiRaw(uint8_t n_bytes, uint8_t* in_buffer, uint8_t* out_buffer, uint8_t can_return_bef_tx)
{
  /* This is used for DMA transfer */
  static uint8_t aux_buff[84];

  S2LPSetSpiInUse(1);

  if((((uint32_t)in_buffer)&0x20000000)!=0x20000000)
  {
    /* Since we are using DMA, if the buffer is not in RAM, copy it in RAM before */
    for(uint8_t i=0;i<n_bytes;i++)
	aux_buff[i]=in_buffer[i];

    /* Call the SPI function of the S2LP_EVAL module perform a generic SPI transaction */
    S2LPSpiRaw(n_bytes, aux_buff, out_buffer, can_return_bef_tx);
  }
  else
  {
    /* Call the SPI function of the S2LP_EVAL module perform a generic SPI transaction */
    S2LPSpiRaw(n_bytes, in_buffer, out_buffer, can_return_bef_tx);
  }
}


/* Monarch Reference Design APIs */

#ifdef MONARCH_REF_DES
void ST_MCU_API_SetExtPAStatus(ExtPaStatus pa_status)
{
  switch (pa_status)
  {
  case SHUTDOWN:
    ExternalPaShutdown();
    break;
  case TX_BYPASS:
    ExternalPaTxBypass();
    break;
  case TX:
    ExternalPaTxActive();
    break;
  case RX:
    ExternalPaRx();
    break;
  default:
    ExternalPaShutdown();
    break;
  }
}
#endif

#ifdef MONARCH_GPIO_SAMPLING
void ST_MCU_API_InitOOKGpio(sfx_u8 pin)
{
  SysCtrl_PeripheralClockCmd(CLOCK_PERIPH_GPIO, ENABLE);

  GPIO_InitType GPIO_InitStructure;
  GPIO_InitStructure.GPIO_Pin = M2S_GPIO_IRQ_PIN;
  GPIO_InitStructure.GPIO_Mode = M2S_GPIO_IRQ_MODE;
  GPIO_InitStructure.GPIO_Pull = M2S_GPIO_IRQ_PUPD;
  GPIO_InitStructure.GPIO_HighPwr = M2S_GPIO_IRQ_HIGH_POWER;
  GPIO_Init(&GPIO_InitStructure);
}

/* Improve scheduled: based on GPIO selected pin */
sfx_u32 ST_MCU_API_CaptureGPIO(sfx_u8 pin)
{
  return (sfx_u32) READ_BIT(GPIO->DATA, GPIO_Pin_21);
}

void ST_MCU_API_Enable16KHzSamplingTimer(void)
{
  NVIC_SetPriority(SysTick_IRQn,   MED_PRIORITY);

  /* Init the embedded timer */
  priv_MFT_Configuration();

  /* Enable MFT interrupts */
  MFT_EnableIT(MFT1, MFT_IT_TNA, ENABLE);

  /* Start MFT timer */
  MFT_Cmd(MFT1, ENABLE);
}

void ST_MCU_API_Disable16KHzSamplingTimer(void)
{
  /* Stop MFT timer */
  /* Disable MFT interrupts */
  MFT_EnableIT(MFT1, MFT_IT_TNA, DISABLE);
  MFT_ClearIT(MFT1, MFT_IT_TNA);
  MFT_Cmd(MFT1, DISABLE);
}

void priv_MFT_Configuration()
{
  MFT_InitType timer_init;
  NVIC_InitType NVIC_InitStructure;

  /* Enable */
  SysCtrl_PeripheralClockCmd(CLOCK_PERIPH_MTFX1, ENABLE);

  /* Init MFT3 in mode 3 */
  /* Clock 1 is from prescaled clock */
  timer_init.MFT_Mode = MFT_MODE_3;
  timer_init.MFT_Clock1 = MFT_PRESCALED_CLK;
  timer_init.MFT_Prescaler = 0;

#if (HS_SPEED_XTAL == HS_SPEED_XTAL_32MHZ)
  timer_init.MFT_CRA = 1953-1; // Rollover at 1952 clock counts for 32Mhz (16385Hz)
#else
  timer_init.MFT_CRA = 973-1; // Rollover at 976 clock counts for 16Mhz
#endif

  MFT_Init(MFT1, &timer_init);

  /* Set counter for timer1 and timer2 */
  /* Rollover at 1952 clock counts for 32Mhz */

#if (HS_SPEED_XTAL == HS_SPEED_XTAL_32MHZ)
  MFT_SetCounter1(MFT1,1953-1); // Rollover at 1952 clock counts for 32Mhz (16385Hz)
#else
  MFT_SetCounter1(MFT1,973-1); // Rollover at 976 clock counts for 16Mhz
#endif

  /* Enable MFT Interrupts */
  NVIC_InitStructure.NVIC_IRQChannel = MFT1A_IRQn;
  NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = LOW_PRIORITY;
  NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE;
  NVIC_Init(&NVIC_InitStructure);
}

void MFT1A_Handler(void)
{
  MFT_ClearIT(MFT1, MFT_IT_TNA);
  ST_MONARCH_API_Timer_CB();
}
#endif /*MONARCH_GPIO_SAMPLING*/
