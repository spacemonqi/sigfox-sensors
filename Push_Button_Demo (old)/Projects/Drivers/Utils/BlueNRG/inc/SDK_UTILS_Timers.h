/**
* @file    SDK_UTILS_Timers.h
* @author  LowPower RF BU - AMG
* @version 4.0.0
* @date    May, 2019
* @brief   SDK timers configuration.
* @details
*
* This module allows the user to easily configure the timers.
* The functions that are provided are limited to the generation of an
* IRQ every time the timer elapses.
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
* <h2><center>&copy; COPYRIGHT 2019 STMicroelectronics</center></h2>
*/

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __SDK_UTILS_TIMERS_H
#define __SDK_UTILS_TIMERS_H

#ifdef __cplusplus
 extern "C" {
#endif

#include <stdint.h>
#include "clock.h"

/**
 * @addtogroup SDK_BLUENRG
 * @{
 */

/**
 * @defgroup SDK_UTILS_Timers            SDK UTILS Timers
 * @brief Management of BlueNRG-1/2 timers.
 * @details See the file <i>@ref SDK_UTILS_Timers.h</i> for more details.
 * @{
 */

/**
* @defgroup SDK_UTILS_Timers_Private_TypesDefinitions           SDK UTILS Timers Private Types Definitions
* @{
*/
typedef enum TimerID_Enum {
  TIMESTAMP_TIMER_ID = 0,
  APPL_TIMER_ID
} TimerID_Type;

typedef void (*TimerCallbackType)(uint32_t time);

typedef struct TIMER_InfoS {
  TimerCallbackType callback;
  uint32_t timeout;
  uint16_t delay;
  uint8_t enabled;
} TIMER_InfoType;

/**
 * @defgroup SDK_UTILS_Timers_Exported_Constants         SDK UTILS Timers Exported Constants
 * @{
 */


/**
 *@}
 */


/**
 * @defgroup SDK_UTILS_Timers_Exported_Macros            SDK UTILS Timers Exported Macros
 * @{
 */


/**
 *@}
 */


/**
 * @defgroup SDK_UTILS_Timers_Exported_Functions         SDK UTILS Timers Exported Functions
 * @{
 */
void SdkDelayMs(volatile uint32_t lTimeMs);
void SdkEvalTimerTimestampReset(void);
void SdkEvalTimersResetCounter(TimerID_Type timerID);
uint32_t SdkEvalTimersState(TimerID_Type timerID, uint8_t enable);
void SdkEvalTimersTimConfig_ms(TimerID_Type timerID, uint16_t ms);
uint32_t SdkEvalGetTimerValue(void);
void SysTick_Handler(void);
uint32_t SdkGetCurrentSysTick(void);
void SdkEvalUpdateTimerValue(void);

/**
 *@}
 */

/**
 *@}
 */

/**
 *@}
 */

#ifdef __cplusplus
}
#endif

#endif /*__SDK_UTIL_TIMERS_H*/

/******************* (C) COPYRIGHT 2019 STMicroelectronics *****END OF FILE****/
