/*!
* \file mcu_api.c
* \brief Sigfox MCU functions
* \author  AMG - RF Application team
* \version 2.3.6
* \date July, 2019
* \copyright COPYRIGHT 2018 STMicroelectronics
*
* This file defines the manufacturer's MCU functions to be implemented
* for library usage.
*/

/********************************************************
* External API dependencies to link with this library.
*
* Error codes of the MCU API functions are described below.
* The Manufacturer can add more error code taking care of the limits defined.
*
********************************************************/

#include "sigfox_stack.h"
#include "SDK_EVAL_Config.h"
#include "SDK_UTILS_Timers.h"
#include "S2LP_Middleware_Config.h"

//#define DEBUG

#ifdef DEBUG
void ST_dbg_CB(const char *vectcStr,...);
#define PRINTF(...)     { ST_dbg_CB(__VA_ARGS__);}
#else
#define PRINTF(...)
#endif

#define DECAY_LEVEL 34

#define ATOMIC_SECTION_BEGIN() uint32_t uwPRIMASK_Bit = __get_PRIMASK(); __disable_irq();

 /* Must be called in the same or in a lower scope of ATOMIC_SECTION_BEGIN */
#define ATOMIC_SECTION_END() __set_PRIMASK(uwPRIMASK_Bit)

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

#define M2S_GPIO_IRQ_PIN			S2LP_Middleware_GpioGetPin((M2SGpioPin)S2LP_GPIO_IRQ_PIN)

#if defined(USE_STM32L0XX_NUCLEO) || defined(USE_STM32F0XX_NUCLEO)
#define IRQ_PRIORITY 0x00
#else
#define IRQ_PRIORITY 0x0A
#endif

#define MCU_API_VER		"v2.3.8"

/** @}*/

static RTC_HandleTypeDef RtcHandler={.Instance=RTC};
static volatile uint8_t rtc_irq=0, rtc_in_use=0, notify_end=0, rtc_in_use_for_cs=0;
static volatile uint8_t low_power=1,carrier_sense_tim_started=0;
static volatile uint32_t next_rtc_wakeup=0,n_intermediate_tim_irq=0;
static volatile int16_t rtc_presc=2375;
static volatile uint8_t s2lp_irq_raised=0;
static TIM_HandleTypeDef  Tim2_Handler={.Instance=TIM2};
static uint8_t _encryptedPayload = 0;
static const uint8_t _libVersion[] = MCU_API_VER;

__weak void Appli_Exti_CB(uint16_t GPIO_Pin);

#ifdef USE_STM32L0XX_NUCLEO
void ST_MCU_API_SetSysClock(void)
{
  RCC_ClkInitTypeDef RCC_ClkInitStruct;
  RCC_OscInitTypeDef RCC_OscInitStruct;

  /* Enable Power Control clock */
  __HAL_RCC_PWR_CLK_ENABLE();

  /* The voltage scaling allows optimizing the power consumption when the device is
  clocked below the maximum system frequency, to update the voltage scaling value
  regarding system frequency refer to product datasheet.  */
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /* Enable HSI Oscillator and activate PLL with HSI as source */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSEState = RCC_HSE_OFF;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLLMUL_4;
  RCC_OscInitStruct.PLL.PLLDIV = RCC_PLLDIV_4;
  RCC_OscInitStruct.HSICalibrationValue = 0x10;
  if(HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
  }

  /* Select PLL as system clock source and configure the HCLK, PCLK1 and PCLK2
  clocks dividers */
  RCC_ClkInitStruct.ClockType = (RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2);
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
  if(HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_1) != HAL_OK)
  {
  }
}
#elif USE_STM32F0XX_NUCLEO
void ST_MCU_API_SetSysClock(void)
{
  RCC_ClkInitTypeDef RCC_ClkInitStruct;
  RCC_OscInitTypeDef RCC_OscInitStruct;

  /* Select HSI48 Oscillator as PLL source */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI48;
  RCC_OscInitStruct.HSI48State = RCC_HSI48_ON;
  //  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI48;
  RCC_OscInitStruct.PLL.PREDIV = RCC_PREDIV_DIV6;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL2;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct)!= HAL_OK)
  {
  }

  /* Select PLL as system clock source and configure the HCLK and PCLK1 clocks dividers */
  RCC_ClkInitStruct.ClockType = (RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_PCLK1);
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_1)!= HAL_OK)
  {
  }

}
#elif USE_STM32F4XX_NUCLEO
void ST_MCU_API_SetSysClock(void)
{
  RCC_ClkInitTypeDef RCC_ClkInitStruct;
  RCC_OscInitTypeDef RCC_OscInitStruct;

  /* Enable Power Control clock */
  __HAL_RCC_PWR_CLK_ENABLE();

  /* The voltage scaling allows optimizing the power consumption when the device is
  clocked below the maximum system frequency, to update the voltage scaling value
  regarding system frequency refer to product datasheet.  */
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE2);

  /* Enable HSI Oscillator and activate PLL with HSI as source */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = 0x10;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLM = 16;
  RCC_OscInitStruct.PLL.PLLN = 64;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV4;
  RCC_OscInitStruct.PLL.PLLQ = 4;
  if(HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
  }

  /* Select PLL as system clock source and configure the HCLK, PCLK1 and PCLK2
  clocks dividers */
  RCC_ClkInitStruct.ClockType = (RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2);
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
  if(HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
  }
}
#else
void ST_MCU_API_SetSysClock(void)
{

  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};

  /* Enable HSE Oscillator and Activate PLL with HSE as source */
  RCC_OscInitStruct.OscillatorType      = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState            = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState        = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource       = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLMUL          = RCC_PLL_MUL4;
  RCC_OscInitStruct.PLL.PLLDIV          = RCC_PLL_DIV4;
  HAL_RCC_OscConfig(&RCC_OscInitStruct);

  /* Set Voltage scale1 as MCU will run at 32MHz */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /* Poll VOSF bit of in PWR_CSR. Wait until it is reset to 0 */
  while (__HAL_PWR_GET_FLAG(PWR_FLAG_VOS) != RESET) {};

  /* Select PLL as system clock source and configure the HCLK, PCLK1 and PCLK2
  clocks dividers */
  RCC_ClkInitStruct.ClockType = (RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2);
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
  HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_1);

}

#endif

static void setGpioLowPower(void)
{
  GPIO_InitTypeDef GPIO_InitStructure;
  GPIO_InitStructure.Mode       = GPIO_MODE_ANALOG;
  GPIO_InitStructure.Pull       = GPIO_NOPULL;
  GPIO_InitStructure.Speed      = GPIO_SPEED_HIGH;

  GPIO_InitStructure.Pin        = EEPROM_SPI_MOSI_PIN | EEPROM_SPI_MISO_PIN;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStructure);

  GPIO_InitStructure.Mode       = GPIO_MODE_ANALOG;
  GPIO_InitStructure.Pull       = GPIO_NOPULL;
  GPIO_InitStructure.Speed      = GPIO_SPEED_HIGH;

  GPIO_InitStructure.Pin        = S2LP_SPI_SCLK_PIN;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStructure);
}

static void setGpioRestore(void)
{
  /* For STM32, restore every gpio, previosly set as analog as digital */

  /* Restore all GPIO CLKs */
  STM32_GPIO_CLK_ENABLE();

  /* SPI_MOSI/MISO */
  GPIO_InitTypeDef GPIO_InitStructure;
  GPIO_InitStructure.Mode       = GPIO_MODE_AF_PP;
  GPIO_InitStructure.Pull       = GPIO_PULLUP;
  GPIO_InitStructure.Speed      = GPIO_SPEED_HIGH;
  GPIO_InitStructure.Alternate  = EEPROM_SPI_MISO_AF;
  GPIO_InitStructure.Pin        = EEPROM_SPI_MOSI_PIN | EEPROM_SPI_MISO_PIN;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStructure);

  /* SPI_CLK*/
  GPIO_InitStructure.Mode       = GPIO_MODE_AF_PP;
  GPIO_InitStructure.Pull       = GPIO_PULLUP;
  GPIO_InitStructure.Alternate  = EEPROM_SPI_MISO_AF;
  GPIO_InitStructure.Pin        = S2LP_SPI_SCLK_PIN;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStructure);

}

static void handleS2LPIRQ(void){
    if (!ST_RF_API_Get_Continuous_TX_or_MONARCH_Scan_Flag())
    {
	/* Avoid to refill the FIFO wile is still filling */
	if (ST_RF_API_GetFIFOState()==ST_FIFO_STATE_WAITING_UNDERFLOW)
	  s2lp_irq_raised=1;
    }
    else
      ST_RF_API_S2LP_IRQ_CB(); //If the CBPSK is implemented trigger TX State Machine
}

void ST_MCU_API_GPIO_LowPower(void){setGpioLowPower();}
void ST_MCU_API_GPIO_Restore(void){setGpioRestore();}

void ST_MCU_API_WaitForInterrupt(void)
{
#ifndef DEBUG
  if(low_power && (!carrier_sense_tim_started))
  {
    setGpioLowPower();

    ATOMIC_SECTION_BEGIN();

    if (!s2lp_irq_raised) {
	HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON,PWR_STOPENTRY_WFI);
	ST_MCU_API_SetSysClock();
    }

    ATOMIC_SECTION_END();

    setGpioRestore();
  }
#endif

  if(s2lp_irq_raised) {
    s2lp_irq_raised=0;
    ST_RF_API_S2LP_IRQ_CB();
  }
}

static void Configure_RTC_Clock(void)
{
  RCC_OscInitTypeDef        RCC_OscInitStruct;
  RCC_PeriphCLKInitTypeDef  PeriphClkInitStruct;

#ifndef USE_STM32L0XX_NUCLEO
  __HAL_RCC_PWR_CLK_ENABLE();
#endif
  HAL_PWR_EnableBkUpAccess();

  RCC_OscInitStruct.OscillatorType =  RCC_OSCILLATORTYPE_LSI | RCC_OSCILLATORTYPE_LSE;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
  RCC_OscInitStruct.LSIState = RCC_LSI_ON;
  RCC_OscInitStruct.LSEState = RCC_LSE_OFF;
  HAL_RCC_OscConfig(&RCC_OscInitStruct);

  PeriphClkInitStruct.PeriphClockSelection = RCC_PERIPHCLK_RTC;
  PeriphClkInitStruct.RTCClockSelection = RCC_RTCCLKSOURCE_LSI;
  HAL_RCCEx_PeriphCLKConfig(&PeriphClkInitStruct);

  /* Enable RTC Clock */
  __HAL_RCC_RTC_ENABLE();

  HAL_NVIC_SetPriority(STM32_RTC_IRQn, 0x01, 0);
  HAL_NVIC_EnableIRQ(STM32_RTC_IRQn);
}

void ST_MCU_API_TimerCalibration(uint16_t duration_ms)
{
  TIM_HandleTypeDef  Tim2_Handler={.Instance=TIM2};
  uint16_t c;
  Configure_RTC_Clock();
  notify_end=1;
  __HAL_RTC_WAKEUPTIMER_CLEAR_FLAG(&RtcHandler, RTC_FLAG_WUTF);
  __HAL_RTC_CLEAR_FLAG(RTC_EXTI_LINE_WAKEUPTIMER_EVENT);

  next_rtc_wakeup=0;

  SdkEvalTimersTimConfig(&Tim2_Handler, 16000-1, 65535-1);
  __HAL_TIM_DISABLE_IT(&Tim2_Handler, TIM_IT_UPDATE);
  HAL_NVIC_DisableIRQ(TIM2_IRQn);
  HAL_TIM_Base_Start(&Tim2_Handler);

  HAL_RTCEx_SetWakeUpTimer_IT(&RtcHandler,rtc_presc*duration_ms/1000,RTC_WAKEUPCLOCK_RTCCLK_DIV16);
  while(!rtc_irq);
  c=Tim2_Handler.Instance->CNT;
  rtc_irq=0;
  HAL_TIM_Base_Stop(&Tim2_Handler);

  rtc_presc=duration_ms*rtc_presc/c;
}

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
  __HAL_GPIO_EXTI_CLEAR_IT(GPIO_Pin);

  if(GPIO_Pin == M2S_GPIO_IRQ_PIN)
    handleS2LPIRQ();
  else
    Appli_Exti_CB(GPIO_Pin);
}

void STM32_RTC_IRQHandler(void)
{
  Configure_RTC_Clock();

  PRINTF("*** RTC_IRQHandler IN\n\r");

  HAL_RTCEx_WakeUpTimerIRQHandler(&RtcHandler);
  HAL_RTCEx_DeactivateWakeUpTimer(&RtcHandler);

  if(next_rtc_wakeup==0)
  {
    rtc_irq=1;
    rtc_in_use=0;
    if(notify_end)
    {
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
  else
  {
    MCU_API_timer_start(next_rtc_wakeup);
    n_intermediate_tim_irq++;
  }
}

void TIM2_IRQHandler(void)
{
  if(__HAL_TIM_GET_IT_SOURCE(&Tim2_Handler, TIM_IT_UPDATE) !=RESET)
  {
    ST_RF_API_Timer_Channel_Clear_CB();

    __HAL_TIM_CLEAR_IT(&Tim2_Handler, TIM_IT_UPDATE);
    SdkEvalTimersState(GP_TIMER_ID, &Tim2_Handler, DISABLE);
  }
}

static void priv_ST_MCU_API_delay(uint32_t delay_ms)
{
  PRINTF("priv_ST_MCU_API_delay IN (%d)\n\r",delay_ms);

  SdkDelayMs(delay_ms);

  PRINTF("priv_ST_MCU_API_delay OUT\n\r");
}

sfx_u8 MCU_API_malloc(sfx_u16 size, sfx_u8 **returned_pointer)
{
  PRINTF("MCU_API_malloc IN\n\r");

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

sfx_u8 MCU_API_free(sfx_u8 *ptr)
{
  PRINTF("MCU_API_free IN\n\r");
  PRINTF("MCU_API_free OUT\n\r");
  return SFX_ERR_NONE;
}

sfx_u8 MCU_API_get_voltage_temperature(sfx_u16 *voltage_idle,
				       sfx_u16 *voltage_tx,
				       sfx_s16 *temperature)
{
  PRINTF("MCU_API_get_voltage_temperature IN\n\r");

  /* get the idle voltage of the complete device
  get the temperature of the device
  if those values are not available : set it to 0x0000
  return the voltage_idle in 1/10 volt on 16bits and 1/10 degrees for the temperature */
  (*voltage_idle)=0;
  (*voltage_tx)=0;
  (*temperature)=0;
  PRINTF("MCU_API_get_voltage_temperature OUT\n\r");

  return SFX_ERR_NONE;
}

sfx_u8 MCU_API_delay(sfx_delay_t delay_type)
{
  PRINTF("MCU_API_delay IN (%d)\n\r", delay_type);

  switch(delay_type)
  {
  case SFX_DLY_INTER_FRAME_TRX:
  case SFX_DLY_INTER_FRAME_TX:
  case SFX_DLY_CS_SLEEP:
    /* ramping should be considered in the ramp up/down:
    since we have 72 samples in the ramp
    (18ms for each ramp, we need to compensate 36 ms)
    Moreover we have also 6ms of silence (2 before and 4 after packet)
    */
    priv_ST_MCU_API_delay(500-2*ST_RF_API_get_ramp_duration());
    break;
  case SFX_DLY_OOB_ACK:
    priv_ST_MCU_API_delay(2000-2*ST_RF_API_get_ramp_duration());
    break;
  }

  PRINTF("MCU_API_delay OUT\n\r");

  return SFX_ERR_NONE;
}

sfx_u8 MCU_API_aes_128_cbc_encrypt(sfx_u8 *encrypted_data,
				   sfx_u8 *data_to_encrypt,
				   sfx_u8 aes_block_len,
				   sfx_u8 key[16],
				   sfx_credentials_use_key_t use_key)
{
  /* Let the retriever encrypts the requested buffer using the ID_KEY_RETRIEVER function.
  The retriever knows the KEY of this node. */
  PRINTF("MCU_API_aes_128_cbc_encrypt IN\n\r");

  enc_utils_encrypt(encrypted_data, data_to_encrypt, aes_block_len, key, use_key);

  PRINTF("MCU_API_aes_128_cbc_encrypt OUT\n\r");

  return SFX_ERR_NONE;
}

sfx_u8 MCU_API_get_nv_mem(sfx_u8 read_data[SFX_NVMEM_BLOCK_SIZE])
{
  PRINTF("MCU_API_get_nv_mem IN\n\r");

  /* Read data */
  NVM_RW_RESULTS res = NVM_ReadRecord((uint8_t *)read_data, SFX_NVMEM_BLOCK_SIZE);

  PRINTF("MCU_API_get_nv_mem OUT\n\r");
  return res;
}

sfx_u8 MCU_API_set_nv_mem(sfx_u8 data_to_write[SFX_NVMEM_BLOCK_SIZE])
{
  PRINTF("MCU_API_set_nv_mem IN\n\r");

  /* Write data */
  NVM_RW_RESULTS res = NVM_WriteRecord((uint8_t *)data_to_write, SFX_NVMEM_BLOCK_SIZE);

  PRINTF("MCU_API_set_nv_mem OUT\n\r");
  return res;
}

sfx_u8 MCU_API_timer_start_carrier_sense(sfx_u16 time_duration_in_ms)
{
  uint32_t rtc_wup_tick, next_rtc_wakeup_tick;
  PRINTF("MCU_API_timer_start_carrier_sense IN (rtc_in_use=%d)\n\r",rtc_in_use);

  carrier_sense_tim_started=1;

  if(rtc_in_use)
  {
    uint32_t n = ((uint32_t)time_duration_in_ms*16000);
    uint16_t a,b;
    SdkEvalTimersFindFactors(n,&a,&b);
    SdkEvalTimersTimConfig(&Tim2_Handler,a-1,b-1);
    SdkEvalTimersState(GP_TIMER_ID, &Tim2_Handler, ENABLE);
  }
  else
  {
    Configure_RTC_Clock();
    notify_end = 1;
    __HAL_RTC_WAKEUPTIMER_CLEAR_FLAG(&RtcHandler, RTC_FLAG_WUTF);
    __HAL_RTC_CLEAR_FLAG(RTC_EXTI_LINE_WAKEUPTIMER_EVENT);
    n_intermediate_tim_irq=0;
    rtc_in_use=1;
    rtc_in_use_for_cs=1;
    //rtc_wup_tick = time_duration_in_ms/1000*rtc_presc;
    rtc_wup_tick = (time_duration_in_ms*rtc_presc)/1000;
    if(rtc_wup_tick>65535) /* Mapped register is 16bit */
    {
      next_rtc_wakeup_tick=rtc_wup_tick-65535;
      rtc_wup_tick=65535;
    }
    else
    {
      next_rtc_wakeup_tick=0;
    }

    //next_rtc_wakeup = next_rtc_wakeup_tick/rtc_presc*1000;
    next_rtc_wakeup = (next_rtc_wakeup_tick*1000)/rtc_presc;
    HAL_RTCEx_SetWakeUpTimer_IT(&RtcHandler, rtc_wup_tick, RTC_WAKEUPCLOCK_RTCCLK_DIV16);
  }

  PRINTF("MCU_API_timer_start_carrier_sense OUT\n\r");

  return SFX_ERR_NONE;
}

sfx_u8 MCU_API_timer_start(sfx_u32 time_duration_in_s)
{
  uint32_t rtc_wup_tick, next_rtc_wakeup_tick;

  ST_RF_API_Timer_CB(TIMER_START); /* To notify the rf_api layer */
  rtc_irq=0;

  if (time_duration_in_s == DECAY_LEVEL)
    time_duration_in_s += 2; /* In order to make RX-PROTOCOL End of Listening Window working */

  PRINTF("MCU_API_timer_start IN %d\n\r", time_duration_in_s);

  Configure_RTC_Clock();
  notify_end=1;
  __HAL_RTC_WAKEUPTIMER_CLEAR_FLAG(&RtcHandler, RTC_FLAG_WUTF);
  __HAL_RTC_CLEAR_FLAG(RTC_EXTI_LINE_WAKEUPTIMER_EVENT);
  n_intermediate_tim_irq=0;
  rtc_in_use=1;

  rtc_wup_tick = (time_duration_in_s)*rtc_presc;

  if(rtc_wup_tick>65535)
  {
    next_rtc_wakeup_tick=(rtc_wup_tick)-65535;
    rtc_wup_tick=65535;
  }
  else
  {
    next_rtc_wakeup_tick=0;
  }

  HAL_RTCEx_SetWakeUpTimer_IT(&RtcHandler,rtc_wup_tick,RTC_WAKEUPCLOCK_RTCCLK_DIV16);

  next_rtc_wakeup=next_rtc_wakeup_tick/rtc_presc;

  PRINTF("MCU_API_timer_start OUT %d\n\r", next_rtc_wakeup);
  return SFX_ERR_NONE;
}

sfx_u8 MCU_API_timer_stop(void)
{
  PRINTF("MCU_API_timer_stop IN\n\r");
  HAL_RTCEx_DeactivateWakeUpTimer(&RtcHandler);
  rtc_in_use=0;
  PRINTF("MCU_API_timer_stop OUT\n\r");
  return SFX_ERR_NONE;
}

sfx_u8 MCU_API_timer_stop_carrier_sense(void)
{
  PRINTF("MCU_API_timer_stop_carrier_sense IN\n\r");

  if(rtc_in_use_for_cs)
  {
    HAL_RTCEx_DeactivateWakeUpTimer(&RtcHandler);
    rtc_in_use=0;
    rtc_in_use_for_cs=0;
  }
  else
  {
    SdkEvalTimersState(GP_TIMER_ID, &Tim2_Handler, DISABLE);
  }
  carrier_sense_tim_started=0;

  PRINTF("MCU_API_timer_stop_carrier_sense OUT\n\r");

  return SFX_ERR_NONE;

}

sfx_u8 MCU_API_timer_wait_for_end(void)
{
  PRINTF("MCU_API_timer_wait_for_end IN\n\r");

  while(!rtc_irq)//(!(next_rtc_wakeup==0 || rtc_irq==1))
  {
    ST_MCU_API_WaitForInterrupt();
  }
  rtc_irq=0;
  PRINTF("MCU_API_timer_wait_for_end OUT\n\r");
  return SFX_ERR_NONE;
}

void ST_MANUF_report_CB(uint8_t status, int32_t rssi);

sfx_u8 MCU_API_report_test_result(sfx_bool status, sfx_s16 rssi)
{

  ST_MANUF_report_CB(status, rssi);
  // use this function to : print output result : status and rssi on uart if you have one or any link is available on device
  // or use a gpio to indicate at least the status
  // or to send a message over the air using any link to report the status with rssi
  // you could also use the RF part in specific modulation (ook ask or gfsk or else to return status and rssi
  return SFX_ERR_NONE;
}

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
  (*payload_encryption_enabled) = _encryptedPayload;
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

void ST_MCU_API_LowPower(sfx_u8 low_power_flag)
{
  low_power=low_power_flag;
}

void ST_MCU_API_GpioIRQ(sfx_u8 new_state, sfx_u8 trigger)
{
  /* configure the MCU IRQ connected to the specified S2-LP GPIO */
  /* trigger 1: rising, 0: falling (default) */
  S2LPIRQEnableEx(new_state, trigger);
}

void ST_MCU_API_Shutdown(sfx_u8 value)
{
  if(value==ST_TRUE)
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
}

void ST_MCU_API_SpiRaw(uint8_t n_bytes, uint8_t* in_buffer, uint8_t* out_buffer, uint8_t can_return_bef_tx)
{
  /* in this implementation we are not interested in the value of the can_return_bef_tx flag.
  We always pass 0 to the S2LPSpiRaw so that the CPU will wait the DMA for the end of transfer. */
  S2LPSpiRaw(n_bytes,in_buffer,out_buffer,0);
}

void ST_MCU_API_SetEncryptionPayload(uint8_t ePayload)
{
  _encryptedPayload = ePayload;
}
