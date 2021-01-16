/**
* @file    Platform_Configuration_STEVAL_IDB00xV2.h
* @author  AMS VMA RF application team
* @version V1.0.0
* @date    December, 2018
* @brief   This file contains definitions for STEVAL-IDB007V2 and STEVAL-IDB008V2 Eval Platform
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

/** Supported configurations:
1) STEVAL-IDB007V1/2 (with hw changes) + STEVAL-FKI868V1/2
2) STEVAL-IDB007V1/2 (with hw changes) + STEVAL-FKI915V1
3) STEVAL-IDB008V1/2 (with hw changes) + STEVAL-FKI868V1/2
4) STEVAL-IDB008V1/2 (with hw changes) + STEVAL-FKI915V1
*/
/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __PLATFORM_CONFIGURATION_STEVAL_IDB00xV2_H
#define __PLATFORM_CONFIGURATION_STEVAL_IDB00xV2_H

/* Includes ------------------------------------------------------------------*/
#include "BlueNRG_x_device.h"
#include "BlueNRG1_conf.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
* @brief MCU UID definition
*/
#define UID_ADDRESS     		_UID_BASE_
#define UID_LEN                             8

/*****************************************************************************/
/*                              BUTTONS SECTION                              */
/*****************************************************************************/
  /**
  * @brief Buttons definitions
  */
#define PUSH_BUTTON1_PIN				GPIO_Pin_13
#define PUSH_BUTTON2_PIN				GPIO_Pin_5


/*****************************************************************************/
/*                              UART SECTION                                 */
/*****************************************************************************/
  /**
  * @brief UART definitions
  */

#define VCOM_YES						0
#define VCOM_NO						1

#define VCOM_PRESENT					VCOM_NO

#define SDK_EVAL_UART_TX_PIN				GPIO_Pin_8
#define SDK_EVAL_UART_TX_MODE				Serial1_Mode
#define SDK_EVAL_UART_TX_PUPD				DISABLE
#define SDK_EVAL_UART_TX_HIGH_POWER			DISABLE

#define SDK_EVAL_UART_RX_PIN				GPIO_Pin_11
#define SDK_EVAL_UART_RX_MODE				Serial1_Mode


/*****************************************************************************/
/*                               I2C SECTION                                 */
/*****************************************************************************/
  /**
  * @brief I2C definitions
  */
#define SDK_EVAL_I2C					I2C2
#define SDK_EVAL_I2C_DATA_PIN				GPIO_Pin_5
#define SDK_EVAL_I2C_DATA_MODE			Serial0_Mode
#define SDK_EVAL_I2C_CLK_PIN				GPIO_Pin_4
#define SDK_EVAL_I2C_CLK_MODE				Serial0_Mode
#define SDK_EVAL_I2C_IRQ_HANDLER			I2C2_Handler
#define SDK_EVAL_I2C_DMA_TX				DMA_CH7
#define SDK_EVAL_I2C_DMA_TX_ITTC			DMA_FLAG_TC7
#define SDK_EVAL_I2C_DMA_RX				DMA_CH6
#define SDK_EVAL_I2C_DMA_RX_ITTC			DMA_FLAG_TC6
#define SDK_EVAL_I2C_BASE				I2C2_BASE


/*****************************************************************************/
/*                               LED SECTION                                 */
/*****************************************************************************/
  /**
  * @brief LEDs definitions
  */
#define SDK_EVAL_LED1_PIN				GPIO_Pin_7 /* On IDB00xV2 GPIO_Pin_6 is allocated for S2-LP SDN */
#define SDK_EVAL_LED2_PIN				GPIO_Pin_7
#define SDK_EVAL_LED3_PIN				GPIO_Pin_14


/*****************************************************************************/
/*                           SPI SENSOR SECTION                              */
/*****************************************************************************/
  /**
  * @brief SPI definitions
  */
#define SDK_EVAL_SPI_PERIPH_SENSOR_PIN		GPIO_Pin_1
#define SDK_EVAL_SPI_PERIPH_SENSOR_MODE		Serial0_Mode

#define SDK_EVAL_SPI_PERIPH_MOSI_PIN		GPIO_Pin_2
#define SDK_EVAL_SPI_PERIPH_MOSI_MODE		Serial0_Mode

#define SDK_EVAL_SPI_PERIPH_MISO_PIN		GPIO_Pin_3
#define SDK_EVAL_SPI_PERIPH_MISO_MODE		Serial0_Mode

#define SDK_EVAL_SPI_PERIPH_SCLK_PIN		GPIO_Pin_0
#define SDK_EVAL_SPI_PERIPH_SCLK_MODE		Serial0_Mode

#define SDK_EVAL_IRQ_SENSOR_PIN			GPIO_Pin_12
#define SDK_EVAL_I2C_IRQ				I2C2_IRQn

#ifdef __cplusplus
}
#endif

#endif /* __PLATFORM_CONFIGURATION_STEVAL_IDB00xV2_H */

/******************* (C) COPYRIGHT 2018 STMicroelectronics *****END OF FILE*****/
