/**
 * @file    SDK_EVAL_Config.h
 * @author  AMS VMA RF application team
 * @version V2.0.0
 * @date    November 29, 2018
 * @brief   This file contains SDK EVAL configuration and useful defines.
 * @details
 *
 * This file is used to include all or a part of the SDK Eval
 * libraries into the application program which will be used.
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


/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __SDK_EVAL_CONFIG_H
#define __SDK_EVAL_CONFIG_H

#ifdef USER_EVAL_PLATFORM
/* Adding the symbol USER_EVAL_PLATFORM an user platform can be supported
 * at compile time, by following these steps:
 *
 * 1) Create a file  "USER_Platform_Configuration.h" with specific user
 *    platform configuration.
 *
 * 2) Place the "USER_Platform_Configuration.h" on the
 *    \Drivers\BSP\SDK_Eval_BlueNRG\inc folder.
 */
  #include "USER_Platform_Configuration.h"
#else
  #ifdef IDB00xV2
  #include "Platform_Configuration_STEVAL_IDB00xV2.h"
  #endif

  #ifdef FKI001V1
  #include "Platform_Configuration_STEVAL_FKI001V1.h"
  #endif

  #ifdef MON_REF_DES
  #include "Platform_Configuration_Monarch_Ref_Design.h"
  #endif
#endif

#include "SDK_EVAL_Button.h"
#include "SDK_EVAL_Com.h"
#include "SDK_EVAL_I2C.h"
#include "SDK_EVAL_Led.h"
#include "SDK_EVAL_SPI.h"

#endif

/******************* (C) COPYRIGHT 2018 STMicroelectronics *****END OF FILE****/
