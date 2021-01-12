/*!
 * \file st_rf_api.h
 * \brief Sigfox manufacturer functions
 * \author  AMG - RF Application team
 * \version 2.7.0
 * \date November 24, 2017
 * \copyright COPYRIGHT 2017 STMicroelectronics
 *
 * This file defines the manufacturer's RF functions to be implemented
 * for library usage.
 */

#ifndef ST_RF_API_H
#define ST_RF_API_H

#include <stdint.h>
#include <stdio.h>
#include <string.h>


#define ST_RF_ERR_API_ERROR                   (sfx_u8)(0x01) /*!< Error on ST_RF_API */

#define TIMER_START  0
#define TIMER_STOP   1

/* macros and defines */
#define PN9_INITIALIZER								0x01FF

/* S2-LP state command codes */
#define CMD_TX									0x60
#define CMD_RX									0x61
#define CMD_READY									0x62
#define CMD_STANDBY								0x63
#define CMD_SABORT								0x67
#define CMD_FLUSHRXFIFO								0x71
#define CMD_FLUSHTXFIFO								0x72
#define DIG_DOMAIN_XTAL_THRESH						30000000
#define MONARCH_DATARATE							16384

/* SPI functions */
#define CMD_STROBE_TX()								priv_ST_MANUF_CmdStrobe(CMD_TX)
#define CMD_STROBE_RX()								priv_ST_MANUF_CmdStrobe(CMD_RX)
#define CMD_STROBE_SRES()							priv_ST_MANUF_CmdStrobe(CMD_SRES)
#define CMD_STROBE_SABORT()							priv_ST_MANUF_CmdStrobe(CMD_SABORT)
#define CMD_STROBE_READY()							priv_ST_MANUF_CmdStrobe(CMD_READY)
#define CMD_STROBE_FRX()							priv_ST_MANUF_CmdStrobe(CMD_FLUSHRXFIFO)
#define CMD_STROBE_FTX()							priv_ST_MANUF_CmdStrobe(CMD_FLUSHTXFIFO)
#define priv_ST_MANUF_ReadFifo(N_BYTES, BUFFER)				priv_ST_MANUF_ReadRegisters(0xFF, N_BYTES, BUFFER)
#define priv_ST_MANUF_SpiRaw_(N_BYTES,BUF_IN,BUF_OUT,BLOCK)		ST_MCU_API_SpiRaw(N_BYTES,BUF_IN,BUF_OUT,BLOCK)
#define priv_ST_MANUF_SpiRaw(N_BYTES,BUF_IN,BUF_OUT)			ST_MCU_API_SpiRaw(N_BYTES,BUF_IN,BUF_OUT,0)

/* variables definition START */
#define ST_RF_API_VER_SIZE	8

//#define BUFF_PLACING const
#define BUFF_PLACING

/* type definition - this represents the state of the library */
typedef enum
{
  ST_MANUF_STATE_IDLE=0,
  ST_MANUF_STATE_TX,
  ST_MANUF_STATE_RX,
  ST_MANUF_STATE_WAIT_TIMER,
  ST_MANUF_STATE_WAIT_CLEAR_CH,
  ST_MANUF_STATE_MONARCH_SCAN
} st_manuf_state_t;


/* type definition - this represents the state of the FIFO of the S2LP */
typedef enum
{
  ST_FIFO_STATE_WAITING_UNDERFLOW=0,
  ST_FIFO_STATE_FILLING
} st_fifo_state_t;

/* type definition - this struct keeps track of the current transmission state */
typedef enum
{
  ST_TX_STATE_NONE=0,
  ST_TX_STATE_RAMP_UP_1,
  ST_TX_STATE_RAMP_UP_2,
  ST_TX_STATE_DATA,
  ST_TX_CONTINUOS_BPSK,
  ST_TX_STATE_RAMP_DOWN_1,
  ST_TX_STATE_RAMP_DOWN_2,
  ST_TX_STATE_RAMP_DOWN_3,
  ST_TX_STATE_STOP
} st_tx_state_t;

/* type definition - this represents the state of the library */
typedef enum
{
  FIFO_RAMP_FAST=0,
  FIFO_CONST_FAST,
  FIFO_RAMP_DOWN_1,
  FIFO_RAMP_DOWN_2,
  FIFO_RAMP_UP_1,
  FIFO_RAMP_UP_2
} st_ramp_buffer_t;

/* type definition - this is used to configure the S2-LP registers according to the role */
typedef enum
{
  TX_MODULATION=0,
  RX_MODULATION
} st_sfx_mod_t;

typedef struct
{
  uint8_t fdev_neg;
  uint8_t fdev_pos;
  uint8_t ramp_start_duration;
  uint8_t min_power;
  uint8_t max_power;
  uint8_t gainFactor1;
  uint8_t gainFactor2;
} ramps_settings_t;

typedef struct
{
  /* TX state structure: collects all the info needed to track the status of the transmission */
  struct
  {
    st_tx_state_t tx_state;
    uint16_t data_to_send_size;
    uint16_t byte_index;
    uint16_t bit_index;
    uint8_t* data_to_send;
    uint16_t current_pn9; //Added to support pn9 continuos
    uint8_t  continuous_tx_monarch_flag; //Accepts data_to send size or not, so send continuosly
  } tx_packet_struct;

  uint8_t last_rssi_reg;
  volatile uint32_t xtal_lib;
  volatile uint32_t priv_xtal_freq;
  volatile uint8_t smps_mode;
  volatile uint8_t tcxo_flag;
  volatile uint8_t pa_flag;
  volatile uint8_t tim_started;
  volatile uint8_t s2lp_irq_raised;
  volatile uint8_t api_timer_raised, api_timer_channel_clear_raised;

  sfx_modulation_type_t radio_conf;
  volatile st_manuf_state_t manuf_state;
  int16_t power_reduction;
  int8_t rssi_offset;
  int8_t lbt_thr_offset;

  /* The tx_is_ready flag is used for CS (ARIB only) and is used in the rf_init for SFX_RF_MODE_CS_RX.
  When the rf_init is called with SFX_RF_MODE_CS_RX, configure also the TX to be faster in case of TX
  */
  uint8_t tx_is_ready;
  uint8_t carrier_sense_tim_nested;
  uint32_t timer_when_stopped,static_time_duration_in_ms;

  /* some zeroes to send null power */
  BUFF_PLACING uint8_t *zeroes;

  /* ramps structures for BPSK modulation */
#ifndef RAMPS_IN_RAM
  /* an auxiliary buffer to:
    - manage the phase change
    - manage the power change
  */
  uint8_t aux_fifo_ramp_fast[82];
#endif

  /* pointers to the ramps to be used */
  ramps_settings_t ramps_settings;

} st_manuf_t;


/*!******************************************************************
 * \fn sfx_u8 ST_RF_API_set_xtal_freq(sfx_u32 xtal)
 * \brief Sets the XTAL frequency of the S2-LP in Hertz (default is 50MHz).
 * \param[in] sfx_u32 xtal: the xtal frequency of the S2-LP in Hz as an integer.
 * \note If this function is not called, the default xtal frequency is 50MHz.
 * \retval 0 if no error, 1 otherwise.
 *******************************************************************/
sfx_u8 ST_RF_API_set_xtal_freq(sfx_u32 xtal);

/*!******************************************************************
 * \fn sfx_u32 ST_RF_API_get_xtal_freq(sfx_u32 *xtal)
 * \brief Gets the RF frequency offset of the  S2-LP XTAL in Hertz.
 * \param[in] sfx_s32* xtal: a pointer to the integer representing the S2-LP XTAL frequency in Hertz.
 * \retval 0 if no error, 1 otherwise.
 *******************************************************************/
sfx_u8 ST_RF_API_get_xtal_freq(sfx_u32 *xtal);

/*!******************************************************************
 * \fn sfx_u8 ST_RF_API_set_rssi_offset(sfx_s8 rssi_off)
 * \brief Set an RSSI offset for the RSSI.
 * \param[in] sfx_s8 rssi_off: an integer representing the offset in dB.
 *                  Default value is 0.
 * \retval 0 if no error, 1 otherwise.
 *******************************************************************/
sfx_u8 ST_RF_API_set_rssi_offset(sfx_s8 rssi_off);

/*!******************************************************************
 * \fn sfx_u8 ST_RF_API_get_rssi_offset(sfx_s8 *rssi_off)
 * \brief Get the RSSI offset for the RSSI.
 * \param[in] sfx_s8* rssi_off: a pointer to the integer representing the offset in dB.
 *                  Default value is 0.
 * \retval 0 if no error, 1 otherwise.
 *******************************************************************/
sfx_u8 ST_RF_API_get_rssi_offset(sfx_s8 *rssi_off);

/*!******************************************************************
 * \fn sfx_u8 ST_RF_API_set_lbt_thr_offset(sfx_s8 lbt_thr_off)
 * \brief Set an offset (dB) for tuning the LBT mechanism.
 * \param[in] sfx_s8 lbt_thr_off: an integer representing the offset in dB.
 *                  Default value is 0.
 * \retval 0 if no error, 1 otherwise.
 *******************************************************************/
sfx_u8 ST_RF_API_set_lbt_thr_offset(sfx_s8 lbt_thr_off);

/*!******************************************************************
 * \fn sfx_u8 ST_RF_API_get_lbt_thr_offset(sfx_s8 *lbt_thr_off)
 * \brief Get the LBT offset (dB) for the LBT mechanism.
 * \param[in] sfx_s8 *lbt_thr_off: a pointer to the integer representing the offset in dB.
 *                  Default value is 0.
 * \retval 0 if no error, 1 otherwise.
 *******************************************************************/
sfx_u8 ST_RF_API_get_lbt_thr_offset(sfx_s8 *lbt_thr_off);

/*!******************************************************************
 * \fn sfx_u8 ST_RF_API_gpio_irq_pin(sfx_u8 gpio_pin)
 * \brief Configures one of the S2-LP pin to be an IRQ pin.
 * \param[in] sfx_u8 gpio_pin: an integer in the range [0,3] representing the GPIO to be used as IRQ.
 *                  Default value is 3.
 * \retval 0 if no error, 1 otherwise.
 *******************************************************************/
sfx_u8 ST_RF_API_gpio_irq_pin(sfx_u8 gpio_pin);

/*!******************************************************************
 * \fn sfx_u8 ST_RF_API_gpio_tx_rx_pin(sfx_u8 gpio_pin)
 * \brief Configures one of the S2-LP pin to be to be configured as (RX or TX) signal.
 * \param[in] sfx_u8 gpio_pin: an integer in the range [0,3] representing the GPIO to be configured as (RX or TX) signal.
 *                  Pass the value 0xFF if the GPIO should not be configured.
 * \retval 0 if no error, 1 otherwise.
 *******************************************************************/
sfx_u8 ST_RF_API_gpio_tx_rx_pin(sfx_u8 gpio_pin);

/*!******************************************************************
 * \fn sfx_u8 ST_RF_API_gpio_rx_pin(sfx_u8 gpio_pin)
 * \brief Configures one of the S2-LP pin to be configured as RX signal.
 * \param[in] sfx_u8 gpio_pin: an integer in the range [0,3] representing the GPIO to be configured as RX signal.
 *                  Pass the value 0xFF if the GPIO should not be configured.
 * \note Only for RCZ2/4. Uneffective for RCZ1. This function must be called before \ref ST_SIGFOX_API_open .
 * \retval 0 if no error, 1 otherwise.
 *******************************************************************/
sfx_u8 ST_RF_API_gpio_rx_pin(sfx_u8 gpio_pin);

/*!******************************************************************
 * \fn sfx_u8 ST_RF_API_gpio_tx_pin(sfx_u8 gpio_pin)
 * \brief Configures one of the S2-LP pin to be configured as TX signal.
 * \param[in] sfx_u8 gpio_pin: an integer in the range [0,3] representing the GPIO to be configured as TX signal.
 *                      Pass the value 0xFF if the GPIO should not be configured.
 * \note Only for RCZ2/4. Uneffective for RCZ1. This function must be called before \ref ST_SIGFOX_API_open .
 * \retval 0 if no error, 1 otherwise.
 *******************************************************************/
sfx_u8 ST_RF_API_gpio_tx_pin(sfx_u8 gpio_pin);

/*!******************************************************************
 * \fn sfx_u8 ST_RF_API_reduce_output_power(sfx_s16 reduction)
 * \brief Reduces the output power of the transmitted signal by a facor (reduction*0.5dB against the actual value).
 * \details       Each positive step of 1 reduces the power at S2-LP level of about 0.5dB. A negative value increase the power level of the same quantity.
 *        <br>The function returns an error if the output power is bigger than the one used dutring cerification.
 * \param[in] sfx_s16 reduction: the reduction factor.
 * \retval 0 if no error, 1 otherwise.
 *******************************************************************/
sfx_u8 ST_RF_API_reduce_output_power(sfx_s16 reduction);

/*!******************************************************************
 * \fn sfx_u8 ST_RF_API_set_tcxo(sfx_u8 tcxo)
 * \brief Instructs the library to configure the S2-LP for a TCXO or for a XTAL.
 * \param[in] sfx_u8 tcxo: 1 if a TCXO, 0 if XTAL.
 * \note If this function is not called, the default is to use the S2-LP in XTAL mode.
 * \retval 0 if no error, 1 otherwise.
 *******************************************************************/
sfx_u8 ST_RF_API_set_tcxo(sfx_u8 tcxo);

/*!******************************************************************
 * \fn sfx_u8 ST_RF_API_smps(sfx_u8 mode)
 * \brief Instructs the library to configure the S2-LP with a user defined smps frequency.
 * \param[in] sfx_u8 mode: from 1 (1.2V) to 7 (1.8V).
 * \note If this function is not called, the default is to use the S2-LP at 1.5V.
 * \retval 0 if no error, 1 otherwise.
 *******************************************************************/
sfx_u8 ST_RF_API_smps(sfx_u8 mode);

/*!******************************************************************
 * \fn sfx_u8 ST_RF_API_set_pa(sfx_u8 pa)
 * \brief Instructs the library to configure the S2-LP for a external PA (Power Amplifier).
 * \param[in] sfx_u8 pa: 1 if a PA, 0 if not.
 * \note If this function is not called, the default is not configure an external PA.
 * \retval 0 if no error, 1 otherwise.
 *******************************************************************/
sfx_u8 ST_RF_API_set_pa(sfx_u8 pa);

/*!******************************************************************
 * \fn sfx_u8 ST_RF_API_get_ramp_duration(void)
 * \brief Returns the duration of the initial (or final) ramp in ms.
 * \param[in] None.
 * \retval Ramp duration in ms.
 *******************************************************************/
sfx_u8 ST_RF_API_get_ramp_duration(void);

/*!******************************************************************
 * \fn void ST_RF_API_S2LP_IRQ_CB(void)
 * \brief This is a <b>callback</b> exported by the RF_API library.
 *      The RF_API module configures the S2-LP to raise interrupts and to notify them
 *      on a GPIO. When the interrupt of that GPIO is raised, this function must be called.
 *      It must be called when the S2-LP raises the IRQ via GPIO.
 * \param[in] None.
 * \retval None.
 *******************************************************************/
void ST_RF_API_S2LP_IRQ_CB(void);

/*!******************************************************************
 * \fn void ST_RF_API_Timer_CB(void)
 * \brief This is a <b>callback</b> exported by the RF_API library.
 *      It must be called when the timer started by \ref MCU_API_timer_start expires.
 * \param[in] sfx_u8 state: 0 for timer start, 1 for timer stop
 * \retval None.
 *******************************************************************/
//void ST_RF_API_Timer_CB(void);
void ST_RF_API_Timer_CB(sfx_u8 state);

/*!******************************************************************
 * \fn void ST_RF_API_Timer_Channel_Clear_CB(void)
 * \brief This is a <b>callback</b> exported by the RF_API library.
 *      It must be called when the timer started by \ref MCU_API_timer_start_carrier_sense expires.
 * \param[in] None.
 * \retval None.
 *******************************************************************/
void ST_RF_API_Timer_Channel_Clear_CB(void);

/*!******************************************************************
 * \fn sfx_u8 ST_RF_API_Get_Continuous_TX_Flag(void);
 * \brief This is a function that give informations abou the tx state MCU API.
 * 		Used for the implementation for continuos BPSK modulation.
 * \param[in] None.
 * \retval 0 IDLE state or TX send frame, 1 Continuos BPSK mode.
 *******************************************************************/
sfx_u8 ST_RF_API_Get_Continuous_TX_or_MONARCH_Scan_Flag(void);

/*!******************************************************************
 * \fn void ST_RF_API_StartTx(void)
 * \brief This is a function to force S2LP to switch in TX mode.
 *      It is called from Monarch detection algorithm.
 * \param[in] None.
 * \retval None.
 *******************************************************************/
sfx_u8 ST_RF_API_StartTx(void);

/*!******************************************************************
 * \fn void ST_RF_API_StartRx(void)
 * \brief This is a function to force S2LP to switch in RX mode.
 *      It is called from Monarch detection algorithm.
 * \param[in] None.
 * \retval None.
 *******************************************************************/
sfx_u8 ST_RF_API_StartRx(void);

/*!******************************************************************
 * \fn void ST_RF_API_StopRxTx(void)
 * \brief This is a function to force S2LP to switch in Ready mode.
 *      It is called from Monarch detection algorithm.
 * \param[in] None.
 * \retval None.
 *******************************************************************/
sfx_u8 ST_RF_API_StopRxTx(void);

/*!******************************************************************
 * \fn void ST_RF_API_GetRSSI(void)
 * \brief This is a function to Get the latest detected RSSI
 *      It is called from Monarch detection algorithm.
 * \param[in] None.
 * \retval RSSI level.
 *******************************************************************/
sfx_s16 ST_RF_API_GetRSSI(void);

/*!******************************************************************
 * \fn void ST_RF_API_ReadFifos(uint8_t address, uint8_t n_bytes, uint8_t* buffer)
 * \brief This is a function to Get the info contained into S2LP rx fifo
 * \param[in] None.
 * \retval RSSI level.
 *******************************************************************/
void ST_RF_API_ReadFifo(sfx_u8 n_bytes, sfx_u8* buffer, sfx_u8 flush);

/*!******************************************************************
 * \fn sfx_u8 ST_RF_API_ReadFifoBytes(void)
 * \brief This is a function to Get the number of bytes into S2LP RX FIFO
 * \param[in] None.
 * \retval number of bytes in RX FIFO.
 *******************************************************************/
sfx_u8 ST_RF_API_ReadFifoBytes(void);

/*!******************************************************************
 * \fn st_fifo_state_t ST_RF_API_GetFIFOState(void)
 * \brief This is a function returns the state of the TX FIFO
 * according to the st_fifo_state_t type.
 * \param[in] None.
 * \retval FIFO state.
 *******************************************************************/
st_fifo_state_t ST_RF_API_GetFIFOState(void);


void ST_RF_API_SetFifoLength(sfx_u8 n_bytes);
void priv_ST_MANUF_generateFIFORampsBuffer(st_ramp_buffer_t bufferType, uint8_t *pBuffer, uint8_t *pBufferSize, ramps_settings_t *rampsSettings);

#endif
