/**
* @file main.c
* @author  AMG - RF Application team
* @version 1.6.0
* @date    December, 2018
* @brief  This is a ST demo that shows how to use the Sigfox protocol to
*         send a message to the base stations each time the push button is pressed.
*         The data sent is a number representing the number of times the button
*	    has been pressed from the boot.
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
* @note       If the application is booted with the push button pressed, it will use the public key for transmission.
* \section KEIL_project KEIL project
To use the project with KEIL uVision 5 for ARM, please follow the instructions below:
-# Open the KEIL uVision 5 for ARM and select Project->Open Project menu.
-# Open the KEIL project
-# Select desired configuration to build
-# Select Project->Rebuild all target files. This will recompile and link the entire application
-# Select Project->Download to download the related binary image.

* \section IAR_project IAR project
To use the project with IAR Embedded Workbench for ARM, please follow the instructions below:
-# Open the Embedded Workbench for ARM and select File->Open->Workspace menu.
-# Open the IAR project
-# Select desired configuration to build
-# Select Project->Rebuild All. This will recompile and link the entire application
-# Select Project->Download and Debug to download the related binary image.

* \subsection Project_configurations Project configurations
- \c NUCLEO_L1 - Configuration to be used for all RCZ on the NUCLEO-L152RE
- \c NUCLEO_L0 - Configuration to be used for all RCZ on the NUCLEO-L053R8
- \c NUCLEO_F0 - Configuration to be used for all RCZ on the NUCLEO-F072RB
- \c NUCLEO_F4 - Configuration to be used for all RCZ on the NUCLEO-F401RE
- \c STEVAL-IDB007V2 - Configuration to be used for all RCZ on the BlueNRG-1 based evaluation board
- \c STEVAL-IDB008V2 - Configuration to be used for all RCZ on the BlueNRG-2 based evaluation board
- \c FKI001V1 - Configuration to be used for all RCZ on the BlueNRG-1 + S2-LP based evaluation board
- \c Monarch Reference Design - Configuration to be used for all RCZ on the BlueNRG-2 + S2-LP based reference design
* \section Board_supported Boards supported
- \c STEVAL-FKI868V2  (for RCZ1 and RCZ3)
- \c STEVAL-FKI915V1  (for RCZ2 and RCZ4)
- \c X-NUCLEO S2868A1 (for RCZ1 and RCZ3)
*
*
* THE PRESENT FIRMWARE WHICH IS FOR GUIDANCE ONLY AIMS AT PROVIDING CUSTOMERS
* WITH CODING INFORMATION REGARDING THEIR PRODUCTS IN ORDER FOR THEM TO SAVE
* TIME. AS A RESULT, STMICROELECTRONICS SHALL NOT BE HELD LIABLE FOR ANY
* DIRECT, INDIRECT OR CONSEQUENTIAL DAMAGES WITH RESPECT TO ANY CLAIMS ARISING
* FROM THE CONTENT OF SUCH FIRMWARE AND/OR THE USE MADE BY CUSTOMERS OF THE
* CODING INFORMATION CONTAINED HEREIN IN CONNECTION WITH THEIR PRODUCTS.
*
* THIS SOURCE CODE IS PROTECTED BY A LICENSE.
* FOR MORE INFORMATION PLEASE CAREFULLY READ THE LICENSE AGREEMENT FILE LOCATED
* IN THE ROOT DIRECTORY OF THIS FIRMWARE PACKAGE.
*
* <h2><center>&copy; COPYRIGHT 2018 STMicroelectronics</center></h2>
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
