/**
* @file    __S2LP_FKI001V1.h
* @author  AMS RF application team
* @version V1.0.0
* @date    December, 2018
* @brief   This file contains definitions for S2LP Shields + Nucleo64 Eval Platforms
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
#ifndef __S2LP_FKI001V1_H
#define __S2LP_FKI001V1_H

/* Includes ------------------------------------------------------------------*/
#include "BlueNRG_x_device.h"
#include "BlueNRG1_conf.h"

#ifdef __cplusplus
extern "C" {
#endif

#define EEPROM_NO								0
#define EEPROM_YES								1

#define S2LP_FEM_NO                             0
#define S2LP_FEM_YES                            1
#define S2LP_FEM_AUTO                           2

/*****************************************************************************/
/*                            GENERAL CONFIG                                 */
/*****************************************************************************/

#define BOARD_VERSION					0x10

/** @brief Definition for XTAL speed (only relevant if EEPROM_PRESENT=EEPROM_NO)
  * XTAL frequency is expressed in Hertz */
#define XTAL_FREQUENCY                  50000000

/** XTAL frequency offset compensation value in Hertz
  * Please, take into account that if nominal frequency is 50 MHz and
  * measured XTAL frequency is (for example) 50000157, then XTAL_FREQUENCY_OFFSET must be
  * set to -157, If not avaialble set it to 0 */
#define XTAL_FREQUENCY_OFFSET                   0

/* This is getting the base frequency from the band defined in the board.
 * For user board, define the desired frequency in Hz (e.g: 868000000) */
#define BOARD_BASE_FREQUENCY                    (S2LPGetFrequencyBand())
#define BOARD_FREQUENCY_BAND                    3 /* 868MHz */

/**
* @brief Definitions for EEPROM
*/
#define EEPROM_PRESENT                          EEPROM_YES

/**
* @brief Definitions for PA
*/
#define S2LP_FEM_PRESENT                        S2LP_FEM_NO

/**
* @brief Definitions for TCXO
*/
#define TCXO_YES                                0
#define TCXO_NO                                 1
#define TCXO_AUTO                               2
#define TCXO_PRESENT                            TCXO_AUTO

/*****************************************************************************/
/*                            S2-LP - SPI CONFIG                             */
/*****************************************************************************/

/**
* @brief SPI definitions
* and connections to S2-LP and EEPROM
*/

/* Defines for chip select pin */
#define S2LP_SPI_CS_PIN					GPIO_Pin_1
#define S2LP_SPI_CS_HIGH_POWER			ENABLE
#define S2LP_SPI_CS_PUPD				ENABLE
#define S2LP_SPI_CS_MODE				GPIO_Output

#define S2LP_SPI_MOSI_PIN				GPIO_Pin_2
#define S2LP_SPI_MOSI_HIGH_POWER			ENABLE
#define S2LP_SPI_MOSI_PUPD				ENABLE
#define S2LP_SPI_MOSI_MODE				Serial0_Mode

#define S2LP_SPI_MISO_PIN				GPIO_Pin_3
#define S2LP_SPI_MISO_HIGH_POWER			ENABLE
#define S2LP_SPI_MISO_PUPD				ENABLE
#define S2LP_SPI_MISO_MODE				Serial0_Mode

#define S2LP_SPI_CLK_PIN				GPIO_Pin_0
#define S2LP_SPI_CLK_HIGH_POWER			ENABLE
#define S2LP_SPI_CLK_PUPD				ENABLE
#define S2LP_SPI_CLK_MODE				Serial0_Mode

/*****************************************************************************/
/*                            S2-LP - EEPROM                                 */
/*****************************************************************************/

/** The EEPROM is an optional component, normally not required in customer's application.
 *  When using a custom board, normally this define should be set to EEPROM_NO.
 *  Since STEVAL kits use EEPROM, set it to EEPROM_YES  */
#define EEPROM_SPI_CS_PIN				GPIO_Pin_6
#define EEPROM_SPI_CS_HIGH_POWER			ENABLE
#define EEPROM_SPI_CS_PUPD				ENABLE
#define EEPROM_SPI_CS_MODE				GPIO_Output

#define EEPROM_SPI_MOSI_PIN				GPIO_Pin_2
#define EEPROM_SPI_MOSI_HIGH_POWER			ENABLE
#define EEPROM_SPI_MOSI_PUPD				ENABLE
#define EEPROM_SPI_MOSI_MODE				Serial0_Mode

#define EEPROM_SPI_MISO_PIN				GPIO_Pin_3
#define EEPROM_SPI_MISO_HIGH_POWER			ENABLE
#define EEPROM_SPI_MISO_PUPD				ENABLE
#define EEPROM_SPI_MISO_MODE				Serial0_Mode

#define EEPROM_SPI_CLK_PIN				GPIO_Pin_0
#define EEPROM_SPI_CLK_HIGH_POWER			ENABLE
#define EEPROM_SPI_CLK_PUPD				ENABLE
#define EEPROM_SPI_CLK_MODE				Serial0_Mode

/*****************************************************************************/
/*                            S2-LP - GPIOs                                  */
/*****************************************************************************/

/* SDN */
#define S2LP_M2S_SDN_PIN				GPIO_Pin_14
#define S2LP_M2S_SDN_HIGH_POWER			DISABLE
#define S2LP_M2S_SDN_PUPD				DISABLE
#define S2LP_M2S_SDN_MODE				GPIO_Output

/**
* @brief Definitions for S2-LP IRQ line
*/
#define S2LP_GPIO_IRQ_PIN				3
#define S2LP_GPIO_IRQ_MODE				S2LP_GPIO_MODE_DIGITAL_OUTPUT_LP

#define M2S_GPIO_IRQ_PIN				GPIO_Pin_13
#define M2S_GPIO_IRQ_SENSE				GPIO_IrqSense_Edge
#define M2S_GPIO_EDGE_EVENT				0 /* 0 means falling edge, 1 raising */
#define M2S_GPIO_IRQ_HIGH_POWER			DISABLE
#define M2S_GPIO_IRQ_PUPD				DISABLE
#define M2S_GPIO_IRQ_MODE				GPIO_Input
#define M2S_GPIO_IRQ_EXTI_MODE			0
#define M2S_GPIO_IRQ_EXTI_PRIORITY			LOW_PRIORITY

/* Only S2-LP GPIO 3 on MCU GPIO 13 is configured */
#define M2S_GPIO_0_PIN					GPIO_Pin_13
#define M2S_GPIO_0_SENSE				GPIO_IrqSense_Edge
#define M2S_GPIO_0_PUPD					DISABLE
#define M2S_GPIO_0_MODE					GPIO_Input
#define M2S_GPIO_0_EXTI_MODE				0
#define M2S_GPIO_0_EXTI_PRIORITY			LOW_PRIORITY

#define M2S_GPIO_1_PIN					GPIO_Pin_13
#define M2S_GPIO_1_SENSE				GPIO_IrqSense_Edge
#define M2S_GPIO_1_PUPD					DISABLE
#define M2S_GPIO_1_MODE					GPIO_Input
#define M2S_GPIO_1_EXTI_MODE				0
#define M2S_GPIO_1_EXTI_PRIORITY			LOW_PRIORITY

#define M2S_GPIO_2_PIN					GPIO_Pin_13
#define M2S_GPIO_2_SENSE				GPIO_IrqSense_Edge
#define M2S_GPIO_2_PUPD					DISABLE
#define M2S_GPIO_2_MODE					GPIO_Input
#define M2S_GPIO_2_EXTI_MODE				0
#define M2S_GPIO_2_EXTI_PRIORITY			LOW_PRIORITY

#define M2S_GPIO_3_PIN					GPIO_Pin_13
#define M2S_GPIO_3_SENSE				GPIO_IrqSense_Edge
#define M2S_GPIO_3_PUPD					DISABLE
#define M2S_GPIO_3_MODE					GPIO_Input
#define M2S_GPIO_3_EXTI_MODE				0
#define M2S_GPIO_3_EXTI_PRIORITY			LOW_PRIORITY

#ifdef __cplusplus
}
#endif

#endif /* __S2LP_FKI001V1_H */

/******************* (C) COPYRIGHT 2018 STMicroelectronics *****END OF FILE*****/
