/**
* @file    S2LP_AUX_FEM_AUTO.c
* @author  LowPower RF BU - AMG
* @version 2.0.0
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
#include "S2LP_Middleware_Config.h"
#include "S2LP_CORE_SPI.h"
#include "S2LP_AUX_FEM.h"
#include "S2LP_AUX_UTILS.h"

/** @addtogroup S2LP_MIDDLEWARE_BLUENRG                           S2LP Middleware - BlueNRG
* @{
*/


/** @defgroup S2LP_AUX_FEM_AUTO						S2LP AUX FEM AUTO
  * @brief  S2-LP FEM handling module.
  * This module exports all the main operations to deal with FEM.
  * @details See the file <i>@ref S2LP_FEM.h</i> for more details.
  * @{
*/


/**
* In order to correctly configure the PA there's need to set the PA Level
* in terms of dBM and the MaxIndex for ramping.
* You can define this functions in your own library
* or include ST's S2LP Library that defines this functions in S2LP_Radio.c
*/
__weak void S2LPRadioSetPALeveldBm(uint8_t cIndex, int32_t wPowerdBm){};
__weak void S2LPRadioSetPALevelMaxIndex(uint8_t cIndex){};

#define PA_CSD_PIN				GPIO_PIN_0
#define PA_CSD_PORT				GPIOA
#define PA_CSD_GPIO_CLK				__GPIOA_CLK_ENABLE

#define PA_CPS_PIN				GPIO_PIN_4
#define PA_CPS_PORT				GPIOA
#define PA_CPS_GPIO_CLK				__GPIOA_CLK_ENABLE

#define PA_CTX_PIN				GPIO_PIN_0
#define PA_CTX_PORT				GPIOB
#define PA_CTX_GPIO_CLK				__GPIOB_CLK_ENABLE

static uint8_t _isBypassEnabled = 0;

/** @defgroup S2LP_AUX_FEM_AUTO_Functions			S2LP AUX FEM Auto exported functions
* @{
*/


/**
* @brief  Front End Module initialization function.
* This function automatically sets the FEM according to the information stored in the device EEPROM.
* This function can be redefined for special needs.
* @param  None
* @retval None
*/
__weak void FEM_Init()
{
  RangeExtType femType = S2LPManagementGetRangeExtender();

  if(femType == RANGE_EXT_NONE)
  {
    /* ... */
  }
  else if(femType == RANGE_EXT_SKYWORKS_SE2435L)
  {
    /* Configuration of S2LP GPIO to control external PA signal CSD, CPS, CTX */
    uint8_t tmp[]={
	(uint8_t)S2LP_GPIO_DIG_OUT_TX_RX_MODE | (uint8_t)S2LP_GPIO_MODE_DIGITAL_OUTPUT_LP,
	(uint8_t)S2LP_GPIO_DIG_OUT_RX_STATE   | (uint8_t)S2LP_GPIO_MODE_DIGITAL_OUTPUT_LP,
	(uint8_t)S2LP_GPIO_DIG_OUT_TX_STATE   | (uint8_t)S2LP_GPIO_MODE_DIGITAL_OUTPUT_LP
    };

    S2LPSpiWriteRegisters(0x00, sizeof(tmp), tmp);
  }
  else if(femType == RANGE_EXT_SKYWORKS_SKY66420)
  {
    /* There is no IDB00xV2 nor FKI001V1 eval board that support this FEM */
  }
}

/**
* @brief  Front End Module Operation function.
* This function configures the PA according to the desired status.
* This function can be redefined for special needs.
* @param  operation Specifies the operation to perform.
*         This parameter can be one of following parameters:
*         @arg FEM_SHUTDOWN: Shutdown PA
*         @arg FEM_TX_BYPASS: Bypass the PA in TX
*         @arg FEM_TX: TX mode
*         @arg FEM_RX: RX mode
* @retval None
*/
__weak void FEM_Operation(FEM_OperationType operation)
{
  RangeExtType femType = S2LPManagementGetRangeExtender();

  FEM_Init();

  switch (operation)
  {
  case FEM_SHUTDOWN: { break; }
  case FEM_TX_BYPASS: { break; }
  case FEM_TX: { break; }
  case FEM_RX: { break; }
  default:
    /* Error */
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
