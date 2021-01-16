/**
 * @file    S2LP_EVAL_FEM_NO.c
 * @author  LowPower RF BU - AMG
 * @version V2.0.0
 * @date    March, 2020
 * @brief   Platform dependent file for external front end module (aka power amplifier)
 *          management. This file is only useful for ST eval kits.
 *          The evaluation kit supported are: STEVAL-FKI868V2 and STEVAL-FKI915V1
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

/* Includes ------------------------------------------------------------------*/
#include "S2LP_AUX_FEM.h"
#include "S2LP_AUX_Utils.h"
#include "S2LP_Middleware_Config.h"

/** @addtogroup S2LP_MIDDLEWARE_BLUENRG                           S2LP Middleware - BlueNRG
* @{
*/


/** @defgroup S2LP_AUX_FEM_NO						S2LP AUX FEM NO
  * @brief  S2-LP FEM handling module.
  * This module exports all the main operations to deal with FEM.
  * @details See the file <i>@ref S2LP_FEM.h</i> for more details.
  * @{
*/


static uint8_t _isBypassEnabled = 0;

/**
 * @brief  Front End Module initialization function.
 * This function does nothing. Dummy implementation.
 * @param  None
 * @retval None
 */
void FEM_Init()
{
}

/**
 * @brief  Front End Module Operation function.
 * This function can be redefined for special needs.
 * @param  operation Specifies the operation to perform.
 *         This parameter can be one of following parameters:
 *         @arg FEM_SHUTDOWN: Shutdown PA
 *         @arg FEM_TX_BYPASS: Bypass the PA in TX
 *         @arg FEM_TX: TX mode
 *         @arg FEM_RX: RX mode
 * @retval None
 */
void FEM_Operation(FEM_OperationType operation)
{
}

/*
* @brief Set the FEM in Bypass (if bypass mode is available)
* This function configures the FEM in Bypass Mode,
* whereas the Bypass mode is available
* @param the Bypass flag (1 means "set Bypass")
* @retval None
*/
void FEM_SetBypass(uint8_t bypass_mode)
{
  _isBypassEnabled = bypass_mode;
}


/*
* @brief Get the FEM Bypass Mode
* This function returns 1 if the FEM is in Bypass Mode
* @param None
* @retval the Bypass state
*/
uint8_t FEM_GetBypass()
{
  return _isBypassEnabled;
}

/**
* @}
*/

/**
* @}
*/


/******************* (C) COPYRIGHT 2020 STMicroelectronics *****END OF FILE****/
