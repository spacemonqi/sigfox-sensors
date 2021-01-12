/**
 * @file    S2LP_TCXO_NO.c
 * @author  LowPower RF BU - AMG
 * @version V1.0.0
 * @date    March, 2020
 * @brief   This file provides implementation of TCXO function when TCXO is not
 * present (dummy functions).
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
 * <h2><center>&copy; COPYRIGHT 2020 STMicroelectronics</center></h2>
 */
#include "S2LP_AUX_TCXO.h"

 /** @addtogroup S2LP_MIDDLEWARE_BLUENRG                           S2LP Middleware - BlueNRG
* @{
*/


/** @defgroup S2LP_AUX_TCXO_NO						S2LP AUX TCXO NO
  * @brief  S2-LP TCXO handling module.
  * This module exports all the main operations to deal with TCXO.
  * @{
*/

/**
 * @brief  TCXO initialization function.
 * This function does nothing. Dummy implementation.
 * @param  None
 * @retval None
 */
void TCXO_Init()
{
}

/**
 * @brief  TCXO Operation function.
 * This function does nothing. Dummy implementation.
 * @param  operation Specifies the operation to perform.
 *         This parameter can be one of following parameters:
 *         @arg TCXO_ON: Turns on TCXO
 *         @arg TCXO_OFF: Turns off TCXO
 * @retval None
 */
void TCXO_Operation(TCXO_OperationType operation)
{
}

/**
* @}
*/

/**
* @}
*/

/******************* (C) COPYRIGHT 2020 STMicroelectronics *****END OF FILE****/
