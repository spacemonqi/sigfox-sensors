/**
* @file    SDK_UTILS_Timers.c
* @author  LowPower RF BU - AMG
* @version 4.0.0
* @date    May, 2019
* @brief   SDK timers configuration.
* @details
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
* <h2><center>&copy; COPYRIGHT 2019 STMicroelectronics</center></h2>
*/


/* Includes ------------------------------------------------------------------*/
#include "SDK_UTILS_Timers.h"

/**
* @addtogroup SDK_UTILS_NUCLEO
* @{
*/

/**
* @addtogroup SDK_UTILS_Timers
* @{
*/

/**
*@}
*/


/**
* @defgroup SDK_UTILS_Timers_Private_Defines                    SDK UTILS Timers Private Defines
* @{
*/

#if ((HS_SPEED_XTAL == HS_SPEED_XTAL_32MHZ)&&(FORCE_CORE_TO_16MHZ != 1))
  #define SYSCLK_FREQ 	32000000            /* System clock frequency */
#elif (HS_SPEED_XTAL == HS_SPEED_XTAL_16MHZ)||(FORCE_CORE_TO_16MHZ == 1)
   #define SYSCLK_FREQ 	16000000            /* System clock frequency */
#else
#error "No definition for SYSCLK_FREQ"
#endif

#define SYST_CLOCK SYSCLK_FREQ
#define CLOCK_FREQUENCY (SYST_CLOCK/1000)
#define CLOCK_FREQUENCY_MHZ (CLOCK_FREQUENCY/1000)

/**
* @brief  Absolute value macro.
* @param  x: Value on which apply the abs function.
* @retval None
*/
#define ABS(x)  (x>0?x:-x)

/**
*@}
*/


/**
* @defgroup SDK_UTILS_Timers_Private_Macros                     SDK UTILS Timers Private Macros
* @{
*/




/**
*@}
*/

/**
* @defgroup SDK_UTILS_Timers_Private_Variables                  SDK UTILS Timers Private Variables
* @{
*/
volatile uint32_t lSystickCounter=0;
static TIMER_InfoType TimerAppliInfo;
volatile uint8_t xApplTimerIRQRaised=0;

/**
*@}
*/

/**
* @defgroup SDK_UTILS_Timers_Private_FunctionPrototypes         SDK UTILS Timers Private Function Prototypes
* @{
*/

/**
*@}
*/


/**
* @defgroup SDK_UTILS_Timers_Private_Functions                  SDK UTILS Timers Private Functions
* @{
*/
static void appliTimerCallback(uint32_t time)
{
  xApplTimerIRQRaised=1;
}

__weak void SysTickUserAction(uint32_t counter)
{
}

/**
* @brief  This function handles SysTick Handler.
* @param  None
* @retval None
*/
void SysTick_Handler(void)
{
  lSystickCounter++;
  if (TimerAppliInfo.enabled && (TimerAppliInfo.timeout == lSystickCounter)) {
    TimerAppliInfo.callback(lSystickCounter);
    TimerAppliInfo.timeout = lSystickCounter + TimerAppliInfo.delay;
  }
  SysTickUserAction(lSystickCounter);
}

/**
* @brief  This function implements return the current
*         systick with a step of 1 ms.
* @param  lTimeMs desired delay expressed in ms.
* @retval None
*/
uint32_t SdkGetCurrentSysTick(void)
{
  return lSystickCounter;
}

/**
* @brief  This function implements a delay using the microcontroller
*         Systick with a step of 1 ms.
* @param  lTimeMs desired delay expressed in ms.
* @retval None
*/
void SdkDelayMs(volatile uint32_t lTimeMs)
{
  uint32_t nWaitPeriod = ~lSystickCounter;

  if(nWaitPeriod<lTimeMs) {
    while( lSystickCounter != 0xFFFFFFFF);
    nWaitPeriod = lTimeMs-nWaitPeriod;
  }
  else
    nWaitPeriod = lTimeMs+ ~nWaitPeriod;

  while( lSystickCounter != nWaitPeriod ) ;
}

void SdkEvalTimerTimestampReset(void)
{
  lSystickCounter = 0;
  SysTick->VAL = 0;
}

uint32_t SdkEvalGetTimerValue(void)
{
  SysTick->CTRL;
  uint32_t reload, ticks;

  do {
    reload = lSystickCounter;
    ticks = SysTick->VAL;
  } while (SysTick->CTRL & SysTick_CTRL_COUNTFLAG_Msk);

  return (reload*1000+(SysTick->LOAD-ticks)/CLOCK_FREQUENCY_MHZ);
}

void SdkEvalTimersTimConfig_ms(TimerID_Type timerID, uint16_t ms)
{
  TimerAppliInfo.enabled = 0;
  TimerAppliInfo.delay = ms;
}

/**
 * @brief  Enables or Disables a specific Timer with its IRQ.
 * @param  TIMER: timer to be set.
 *          This parameter can be a pointer to @ref TIM_TypeDef
 * @param  NEWSTATE: specifies if a timer has to be enabled or disabled.
 *          This parameter is a float.
 * @retval None
 */
uint32_t SdkEvalTimersState(TimerID_Type timerID, uint8_t enable)
{
  uint32_t return_value = 0;
  if (enable) {
    TimerAppliInfo.enabled = 0;
    TimerAppliInfo.timeout = SdkGetCurrentSysTick() + TimerAppliInfo.delay;
    return_value = TimerAppliInfo.timeout;
    TimerAppliInfo.callback = appliTimerCallback;
    TimerAppliInfo.enabled = 1;
  } else {
    TimerAppliInfo.enabled = 0;
  }
  return return_value;
}

void SdkEvalTimersResetCounter(TimerID_Type timerID) { }

void SdkEvalUpdateTimerValue(){}
/**
*@}
*/


/**
*@}
*/


/**
*@}
*/


/******************* (C) COPYRIGHT 2019 STMicroelectronics *****END OF FILE****/
