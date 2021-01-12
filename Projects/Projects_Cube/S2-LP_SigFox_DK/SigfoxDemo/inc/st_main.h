#ifndef _ST_MAIN_H
#define _ST_MAIN_H

/**
* @file    st_main.h
* @author  AMG RF
* @version V1.6.0
* @date    Feb, 2019
* @brief   Command line DEMO program
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
#include "assert.h"

/* ST Init */
#include "ST_Sigfox_Init.h"
#include "ST_Init.h"

/* Sigfox includes */
#include "sigfox_stack.h"

/* Load all SDK layers */
#include "SDK_EVAL_Config.h"
#include "SDK_UTILS_Config.h"
#include "S2LP_Middleware_Config.h"

/* Functions Prototypes-------------------------------------------------------*/
void Appli_Exti_CB(uint32_t GPIO_Pin);

#endif //_ST_MAIN_H


