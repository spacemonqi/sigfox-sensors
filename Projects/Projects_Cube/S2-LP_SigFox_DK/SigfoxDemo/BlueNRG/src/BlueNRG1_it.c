/**
******************************************************************************
* @file    BlueNRG1_it.c
* @author  RF Application Team
* @version V1.0.0
* @date    December, 2018
* @brief   Main Interrupt Service Routines.
*          This file provides an implementation for all exceptions handler and
*          peripherals interrupt service routine.
******************************************************************************
* @attention
*
* THE PRESENT FIRMWARE WHICH IS FOR GUIDANCE ONLY AIMS AT PROVIDING CUSTOMERS
* WITH CODING INFORMATION REGARDING THEIR PRODUCTS IN ORDER FOR THEM TO SAVE
* TIME. AS A RESULT, STMICROELECTRONICS SHALL NOT BE HELD LIABLE FOR ANY
* DIRECT, INDIRECT OR CONSEQUENTIAL DAMAGES WITH RESPECT TO ANY CLAIMS ARISING
* FROM THE CONTENT OF SUCH FIRMWARE AND/OR THE USE MADE BY CUSTOMERS OF THE
* CODING INFORMATION CONTAINED HEREIN IN CONNECTION WITH THEIR PRODUCTS.
*
* <h2><center>&copy; COPYRIGHT 2015 STMicroelectronics</center></h2>
******************************************************************************
*/

/* Includes ------------------------------------------------------------------*/
#include "BlueNRG1_it.h"
#include "BlueNRG1_conf.h"
#include "SDK_EVAL_Config.h"
#include "S2LP_Middleware_Config.h"

#include "clock.h"

void Appli_Exti_CB(uint16_t GPIO_Pin);
void ST_RF_API_S2LP_IRQ_CB(void);

/** @addtogroup BlueNRG1_StdPeriph_Examples
* @{
*/

/** @addtogroup SPI_Examples SPI Examples
* @{
*/

/** @addtogroup SPI_Master_Polling SPI Master Polling
* @{
*/

/* Private typedef -----------------------------------------------------------*/
/* Private define ------------------------------------------------------------*/
/* Private macro -------------------------------------------------------------*/
/* Private variables ---------------------------------------------------------*/
/* Private function prototypes -----------------------------------------------*/
/* Private functions ---------------------------------------------------------*/

/******************************************************************************/
/*            Cortex-M0 Processor Exceptions Handlers                         */
/******************************************************************************/

/**
* @brief  This function handles NMI exception.
*/
void NMI_Handler(void)
{
}

/**
* @brief  This function handles Hard Fault exception.
*/
void HardFault_Handler(void)
{
  /* Go to infinite loop when Hard Fault exception occurs */
  while (1)
  {}
}

/**
* @brief  This function handles SVCall exception.
*/
void SVC_Handler(void)
{
}

/**
* @brief  This function handles PPP interrupt request.
* @param  None
* @retval None
*/
void PPP_IRQHandler(void)
{
}

void GPIO_Handler(void)
{
  if(GPIO_GetITPendingBit(M2S_GPIO_IRQ_PIN)){
    ST_RF_API_S2LP_IRQ_CB();
    GPIO_ClearITPendingBit(M2S_GPIO_IRQ_PIN);
  }
  else if(GPIO_GetITPendingBit(Get_ButtonGpioPin(BUTTON_2))) {
    Appli_Exti_CB(Get_ButtonGpioPin(BUTTON_2));
    GPIO_ClearITPendingBit(Get_ButtonGpioPin(BUTTON_2));
  }
}

void Blue_Handler(void)
{

}
/**
* @}
*/

/**
* @}
*/

/******************* (C) COPYRIGHT 2018 STMicroelectronics *****END OF FILE****/
