/**
* @file main.c
* This application demonstrates interfacing a DHT11 sensor to the S2LP chip, and sending the data via Sigfox to AWS.
* @details
* This application sets the MCU in low power. in order to debug it using a SWD debugger it is necessary to:
* - call the following function in the initialization phase:
* \code
* ST_MCU_API_LowPower(0);
* \endcode
* - comment out the following lines.
* \code
* ST_MCU_API_GPIO_LowPower();
* HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON,PWR_STOPENTRY_WFI);
* ST_MCU_API_SetSysClock();
* ST_MCU_API_GPIO_Restore();
* \endcode
*
* \section IAR_project IAR project
To use the project with IAR Embedded Workbench for ARM, please follow the instructions below:
-# Open the Embedded Workbench for ARM and select File->Open->Workspace menu.
-# Open the IAR project
-# Select desired configuration to build
-# Select Project->Rebuild All. This will recompile and link the entire application
-# Select Project->Download and Debug to download the related binary image.
*
*/

#include "st_main.h"

#ifdef USE_FLASH
#include <string.h>
#endif

/* a flag to understand if the button has been pressed */
static volatile uint8_t but_pressed=0;

void Appli_Exti_CB(uint32_t GPIO_Pin)
{
  /* set the button pressed flag */
  but_pressed=1;
}

/**
* @brief  Blink the LED indefinitely stucking the application.
* @param  None
* @retval None
*/
void Fatal_Error(void)
{
  SdkEvalLedInit(LED2);

  while(1)
  {
    SdkDelayMs(100);
    SdkEvalLedToggle(LED2);
  }
}

/**
* @brief  Let the application led blinks.
* @param  times Number of toggles.
* @retval None
*/
void LedBlink(SdkEvalLed led, uint8_t times)
{
  SdkEvalLedInit(led);

  for(uint8_t i=0;i<times;i++)
  {
    SdkEvalLedToggle(led);
    SdkDelayMs(50);
  }

  SdkEvalLedOn(led);
}

/**
* @brief  System main function.
* @param  None.
* @retval The function never returns.
*/
int main(void)
{
  /* Some local variables to handle the workflow */
  ST_SFX_ERR stSfxRetErr;
  uint8_t ret_err, use_public_key = 0;

  /* Some variables to store the application data to transmit */
  uint32_t cust_counter=0;
  uint8_t customer_data[12]={0};
  uint8_t customer_resp[8];

  /* System initialization function */
  ret_err = ST_Init();

  if(ret_err)
    Fatal_Error();

  SdkDelayMs(10); //Wait for CS to rise

  /* Reset S2LP */
  S2LPShutdownEnter();
  SdkDelayMs(10);
  S2LPShutdownExit();

  /* Set the Push Button 2 as an input. If the application is started with the
  PUSH BUTTON 2 pressed, the public KEY is used by the applicaiton.
  This is useful for testing purposes or to use the SNEK emulator to receive
  Sigfox messages. */
  if (ButtonInit())
  {
    use_public_key=1;
    LedBlink(LED3, 1);

    while(IsButtonPressed());	/* Wait until button is pressed */

    LedBlink(LED3, 1);
  }

/* Only for STM32 eval platforms */
#if  !(defined(BLUENRG2_DEVICE) || defined(BLUENRG1_DEVICE))
  /* The low level driver uses the internal RTC as a timer while the STM32 is in low power.
  This function calibrates the RTC using an auxiliary general purpose timer in order to
  increase its precision. */
  ST_MCU_API_TimerCalibration(500);
#endif

  /* Initialize push button 2 on the board as an interrupt */
  ButtonSetIRQ();

  if(S2LPEvalGetHasEeprom())
  {
    /* Shutdown S2-LP in order to read EEPROM */
    ST_MCU_API_Shutdown(1);
    SdkDelayMs(1);

    /* Set EEPROM CS */
#if  !(defined(BLUENRG2_DEVICE) || defined(BLUENRG1_DEVICE))
    if(SdkEvalGetDaughterBoardType() == FKI_SERIES)
	EepromCsPinInitialization();
    else
	EepromCsXnucleoPinInitialization();
#else
    /* On BlueNRG-1/2 kits the only platform that supports EEPROM kit is the FKI001V1 */
#ifdef FKI001V1
    EepromCsPinInitialization();
#endif
#endif
  }

  /* Init the Sigfox Library and the device for Sigfox communication*/
  NVM_BoardDataType boardData;
  stSfxRetErr = ST_Sigfox_Init(&boardData, 1);

  if(stSfxRetErr != ST_SFX_ERR_NONE)
    Fatal_Error();

  if(use_public_key)
    enc_utils_set_public_key(1);

  SdkEvalLedInit(LED1);
  SdkEvalLedOn(LED1);

  /* application main loop */
  while(1)
  {
#if  !(defined(BLUENRG2_DEVICE) || defined(BLUENRG1_DEVICE))
    /* Go in low power with the STM32 waiting for an external interrupt */
    ST_MCU_API_GPIO_LowPower();
    HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON,PWR_STOPENTRY_WFI);
    ST_MCU_API_SetSysClock();
    ST_MCU_API_GPIO_Restore();
#endif

    if(but_pressed)
    {
      LedBlink(LED3, 6);

      /* If the interrupt is raised, prepare the buffer to send with a 4-bytes counter */
      cust_counter++;

	for(uint8_t i=0;i<4;i++)
	  customer_data[i]=(uint8_t)(cust_counter>>((3-i)*8));

      /* Call the send_frame function */
      SIGFOX_API_send_frame(customer_data,4,customer_resp,2,0);

      LedBlink(LED3, 6);
      but_pressed=0;
    }
  }
}

#ifdef  USE_FULL_ASSERT
/**
* @brief  Reports the name of the source file and the source line number
*         where the assert_param error has occurred.
* @param file: pointer to the source file name
* @param line: assert_param error line source number
* @retval : None
*/
void assert_failed(uint8_t* file, uint32_t line)
{
  /* User can add his own implementation to report the file name and line number */
  //printf("Wrong parameters value: file %s on line %d\r\n", file, line);

  /* Infinite loop */
  while (1)
  {
  }
}
#endif


/******************* (C) COPYRIGHT 2018 STMicroelectronics *****END OF FILE*****/
