/**
 * @file    S2LP_FEM_MoanrchRefDesign.c
 * @author  LowPower RF BU - AMG
 * @version V2.0.0
 * @date    March, 2020
 * @brief   Platform dependent file for external front end module (aka power amplifier)
 *          management
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
#include "BlueNRG1_conf.h"
#include "S2LP_AUX_FEM.h"
#include "S2LP_Middleware_Config.h"

/** @addtogroup S2LP_MIDDLEWARE_BLUENRG           S2LP Middleware - BlueNRG
* @{
*/


/** @defgroup S2LP_AUX_FEM_STDES-MONARCH						S2LP AUX FEM STDES-MONARCH
  * @brief  S2-LP FEM handling module.
  * This module exports all the main operations to deal with FEM.
  * @details See the file <i>@ref S2LP_FEM.h</i> for more details.
  * @{
*/


#define MONARCH_SKY66420_CPS_PIN		GPIO_Pin_23
#define MONARCH_SKY66420_CSD_PIN		GPIO_Pin_24
#define MONARCH_SKY66420_CTX_PIN		GPIO_Pin_22

static uint8_t _isBypassEnabled = 0;

/** @defgroup S2LP_AUX_FEM_STDES-MONARC_Functions			S2LP AUX FEM STDES-MONARCH exported functions
* @{
*/

/**
 * @brief  Front End Module initialization function.
 * This function sets the FEM in order to work with the Monarch Reference Design.
 * @param  None
 * @retval None
 */
void FEM_Init()
{
  GPIO_InitType GPIO_InitStructure;

  GPIO_InitStructure.GPIO_Pin = MONARCH_SKY66420_CPS_PIN | MONARCH_SKY66420_CSD_PIN | MONARCH_SKY66420_CTX_PIN;
  GPIO_InitStructure.GPIO_Mode = GPIO_Output;
  GPIO_InitStructure.GPIO_Pull = DISABLE;
  GPIO_InitStructure.GPIO_HighPwr = DISABLE;
  GPIO_Init(&GPIO_InitStructure);
}

/**
 * @brief  Front End Module Operation function.
 * This function configures the PA according to the desired status.
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
  switch (operation)
  {
    case FEM_SHUTDOWN:
      GPIO_WriteBit(MONARCH_SKY66420_CPS_PIN, Bit_RESET);
      GPIO_WriteBit(MONARCH_SKY66420_CSD_PIN, Bit_RESET); //Shutdown PIN=0
      GPIO_WriteBit(MONARCH_SKY66420_CTX_PIN, Bit_RESET);
      break;
    case FEM_TX_BYPASS:
      GPIO_WriteBit(MONARCH_SKY66420_CPS_PIN, Bit_RESET);  //Bypass mode select
      GPIO_WriteBit(MONARCH_SKY66420_CSD_PIN, Bit_SET);    //Turned on CSD=1
      GPIO_WriteBit(MONARCH_SKY66420_CTX_PIN, Bit_SET);    //TX state = 1
      break;
    case FEM_TX:
	/* Check Bypass mode */
	if (FEM_GetBypass())
	  GPIO_WriteBit(MONARCH_SKY66420_CPS_PIN, Bit_RESET);  //Bypass mode select
	else
	  GPIO_WriteBit(MONARCH_SKY66420_CPS_PIN, Bit_SET);

	GPIO_WriteBit(MONARCH_SKY66420_CSD_PIN, Bit_SET);    //Turned on CSD=1
      GPIO_WriteBit(MONARCH_SKY66420_CTX_PIN, Bit_SET);    //TX state = 1
      break;
    case FEM_RX:
      GPIO_WriteBit(MONARCH_SKY66420_CPS_PIN, Bit_RESET);
      GPIO_WriteBit(MONARCH_SKY66420_CSD_PIN, Bit_SET);    //Turned on CSD=1
      GPIO_WriteBit(MONARCH_SKY66420_CTX_PIN, Bit_RESET);  //TX state = 0
      break;
    default:
      /* !!!Error */
      break;
  }
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

/**
* @}
*/

/******************* (C) COPYRIGHT 2020 STMicroelectronics *****END OF FILE****/
