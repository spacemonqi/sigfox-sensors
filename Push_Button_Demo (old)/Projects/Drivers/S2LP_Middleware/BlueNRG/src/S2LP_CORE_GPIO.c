/**
 * @file    S2LP_CORE_GPIO.c
 * @author  LowPower RF BU - AMG
 * @version 4.0.1
 * @date    May, 2020
 * @brief   This file provides all the low level API to manage SDK eval pin to drive GPIOs.
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
 *
 */

/* Includes ------------------------------------------------------------------*/
#include "SDK_EVAL_Config.h"
#include "S2LP_Middleware_Config.h"
#include "S2LP_CORE_GPIO.h"

/** @addtogroup S2LP_CORE_BLUENRG                     S2LP CORE - BlueNRG
* @{
*/


/** @defgroup S2LP_CORE_GPIO					S2LP CORE GPIO
  * @brief  S2-LP GPIO handling module.
  * This module exports all the main operations to deal with GPIO.
  * @details See the file <i>@ref S2LP_CORE_GPIO.h</i> for more details.
  * @{
*/

/** @defgroup S2LP_CORE_GPIO_Functions			S2LP CORE GPIO exported functions
* @{
*/


/**
 * @brief  M2S GPio Pin array
 */
static const uint32_t s_vectnM2SGpioPin[4] = {
        M2S_GPIO_0_PIN,
        M2S_GPIO_1_PIN,
        M2S_GPIO_2_PIN,
        M2S_GPIO_3_PIN
};

/**
 * @brief  M2S GPio PuPd array
 */
static const uint32_t s_vectxM2SGpioPuPd[4] = {
        M2S_GPIO_0_PUPD,
        M2S_GPIO_1_PUPD,
        M2S_GPIO_2_PUPD,
        M2S_GPIO_3_PUPD
};

/**
 * @brief  M2S Exti Mode array
 */
static const uint32_t s_vectxM2sGpioExtiMode[4] = {
        M2S_GPIO_0_EXTI_MODE,
        M2S_GPIO_1_EXTI_MODE,
        M2S_GPIO_2_EXTI_MODE,
        M2S_GPIO_3_EXTI_MODE
};

/**
 * @brief  Configures MCU GPIO and EXTI Line for GPIOs.
 * @param  xGpio Specifies the GPIO to be configured.
 *         This parameter can be one of following parameters:
 *         @arg M2S_GPIO_0: GPIO_0
 *         @arg M2S_GPIO_1: GPIO_1
 *         @arg M2S_GPIO_2: GPIO_2
 *         @arg M2S_GPIO_3: GPIO_3
 *         @arg M2S_GPIO_SDN: GPIO_SDN
 * @param  xGpioMode Specifies GPIO mode.
 *         This parameter can be one of following parameters:
 *         @arg M2S_MODE_GPIO_IN: MCU GPIO will be used as simple input.
 *         @arg M2S_MODE_EXTI_IN: MCU GPIO will be connected to EXTI line with interrupt
 *         generation capability.
 *         @arg M2S_MODE_GPIO_OUT: MCU GPIO will be used as simple output.
 * @retval None.
 */
void S2LP_Middleware_GpioInit(M2SGpioPin xGpio, M2SGpioMode xGpioMode)
{
  GPIO_InitType GPIO_InitStructure;

  /* Check the parameters */
  assert_param(IS_M2S_GPIO_PIN(xGpio));
  assert_param(IS_M2S_GPIO_MODE(xGpioMode));

  /* Configures MCU GPIO */
  switch (xGpioMode) {
  case M2S_MODE_GPIO_OUT:
    GPIO_InitStructure.GPIO_Mode = GPIO_Output;
    break;
  case M2S_MODE_GPIO_IN:
    GPIO_InitStructure.GPIO_Mode = GPIO_Input;
    break;
  case M2S_MODE_EXTI_IN:
    GPIO_InitStructure.GPIO_Mode = s_vectxM2sGpioExtiMode[xGpio];
    break;
  default:
    break;
  }

  SysCtrl_PeripheralClockCmd(CLOCK_PERIPH_GPIO, ENABLE);

  GPIO_InitStructure.GPIO_Pin = s_vectnM2SGpioPin[xGpio];
  GPIO_InitStructure.GPIO_Pull = (FunctionalState)s_vectxM2SGpioPuPd[xGpio];
  GPIO_InitStructure.GPIO_HighPwr = DISABLE;
  GPIO_Init(&GPIO_InitStructure);

  if (xGpioMode == M2S_MODE_EXTI_IN)
  {
    GPIO_EXTIConfigType GPIO_EXTIStructure;

    GPIO_EXTIStructure.GPIO_Pin = s_vectnM2SGpioPin[xGpio];
    GPIO_EXTIStructure.GPIO_IrqSense = M2S_GPIO_IRQ_SENSE;
    GPIO_EXTIStructure.GPIO_Event = M2S_GPIO_EDGE_EVENT; //0 means falling edge, 1 raising
    GPIO_EXTIConfig(&GPIO_EXTIStructure);

    GPIO_ClearITPendingBit(s_vectnM2SGpioPin[xGpio]);

    GPIO_EXTICmd(s_vectnM2SGpioPin[xGpio], ENABLE);
  }
}

/**
 * @brief  Enables or disables the interrupt on GPIO .
 * @param  xGpio Specifies the GPIO whose priority shall be changed.
 *         This parameter can be one of following parameters:
 *         @arg M2S_GPIO_0: GPIO_0
 *         @arg M2S_GPIO_1: GPIO_1
 *         @arg M2S_GPIO_2: GPIO_2
 *         @arg M2S_GPIO_3: GPIO_3
 * @param  nPreemption Specifies Preemption Priority.
 * @param  nSubpriority Specifies Subgroup Priority.
 * @param  xNewState Specifies the State.
 *         This parameter can be one of following parameters:
 *         @arg 0: Interrupt is disabled
 *         @arg any value != 0: Interrupt is enabled
 * @retval None.
 */
void S2LP_Middleware_GpioInterruptCmd(M2SGpioPin xGpio, uint8_t nPreemption, uint8_t nSubpriority, uint8_t enable, uint8_t edge_direction)
{
  GPIO_EXTIConfigType GPIO_EXTIStructure;

  FunctionalState newState = enable ? ENABLE:DISABLE;

  /* Configures EXTI line */
  GPIO_EXTIStructure.GPIO_Pin = s_vectnM2SGpioPin[xGpio];
  GPIO_EXTIStructure.GPIO_IrqSense = M2S_GPIO_IRQ_SENSE;
  GPIO_EXTIStructure.GPIO_Event = edge_direction; //0 means falling edge, 1 raising

  GPIO_EXTIConfig(&GPIO_EXTIStructure);

  GPIO_EXTICmd(s_vectnM2SGpioPin[xGpio], newState);

  GPIO_ClearITPendingBit(s_vectnM2SGpioPin[xGpio]);

  /* Set the GPIO interrupt priority and enable/disable it */
  if(newState == ENABLE)
  {
    NVIC_InitType NVIC_InitStructure;

    NVIC_InitStructure.NVIC_IRQChannel = GPIO_IRQn;
    NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = M2S_GPIO_IRQ_EXTI_PRIORITY;
    NVIC_InitStructure.NVIC_IRQChannelCmd = newState;

    NVIC_Init(&NVIC_InitStructure);
  }
}

/**
 * @brief  Enables or disables trigger on rising edge for that GPIO .
 * @param  xGpio Specifies the GPIO.
 *         This parameter can be one of following parameters:
 *         @arg M2S_GPIO_0: GPIO_0
 *         @arg M2S_GPIO_1: GPIO_1
 *         @arg M2S_GPIO_2: GPIO_2
 *         @arg M2S_GPIO_3: GPIO_3
 * @param  xNewState Specifies the State.
 *         This parameter can be one of following parameters:
 *         @arg not 0: Rising trigger is enabled
 *         @arg 0: Rising trigger is disabled
 * @retval None.
 */
void S2LP_Middleware_GpioTriggerRising(M2SGpioPin xGpio, uint8_t enable)
{
  GPIO_EXTIConfigType GPIO_EXTIStructure;

  /* Configures EXTI line */

  GPIO_EXTIStructure.GPIO_Pin = s_vectnM2SGpioPin[xGpio];
  GPIO_EXTIStructure.GPIO_IrqSense = GPIO_IrqSense_Edge;
  GPIO_EXTIStructure.GPIO_Event = (uint8_t)enable; //0 means falling edge, 1 raising
  GPIO_EXTIConfig(&GPIO_EXTIStructure);
}

/**
 * @brief  To assert if the rising edge IRQ is enabled for that GPIO .
 * @param  xGpio Specifies the GPIO.
 *         This parameter can be one of following parameters:
 *         @arg M2S_GPIO_0: GPIO_0
 *         @arg M2S_GPIO_1: GPIO_1
 *         @arg M2S_GPIO_2: GPIO_2
 *         @arg M2S_GPIO_3: GPIO_3
 * @retval  Specifies the State.
 *         @arg ENABLE: Rising trigger is enabled
 *         @arg DISABLE: Rising trigger is disabled
 */
uint8_t S2LP_Middleware_GetTriggerRising(M2SGpioPin xGpio)
{
  uint32_t GPIO_Pin = s_vectnM2SGpioPin[xGpio];
  uint8_t edge = READ_BIT(GPIO->IS, GPIO_Pin) == 0;
  uint8_t both_edge = READ_BIT(GPIO->IBE, GPIO_Pin) == 1;
  uint8_t falling = READ_BIT(GPIO->IEV, GPIO_Pin) == 0;

  if (edge && !(both_edge))
    return falling ? 0 : 1;
  else
    return 0;
}

/**
 * @brief  Enables or disables trigger on falling edge for that GPIO .
 * @param  xGpio Specifies the GPIO.
 *         This parameter can be one of following parameters:
 *         @arg M2S_GPIO_0: GPIO_0
 *         @arg M2S_GPIO_1: GPIO_1
 *         @arg M2S_GPIO_2: GPIO_2
 *         @arg M2S_GPIO_3: GPIO_3
 * @param  xNewState Specifies the State.
 *         This parameter can be one of following parameters:
 *         @arg ENABLE: Falling trigger is enabled
 *         @arg DISABLE: Falling trigger is disabled
 * @retval None.
 */
void S2LP_Middleware_GpioTriggerFalling(M2SGpioPin xGpio, uint8_t enable)
{
  GPIO_EXTIConfigType GPIO_EXTIStructure;

  if(enable)
  {
    /* Configures EXTI line */
    GPIO_EXTIStructure.GPIO_Pin = s_vectnM2SGpioPin[xGpio];
    GPIO_EXTIStructure.GPIO_IrqSense = GPIO_IrqSense_Edge;
    GPIO_EXTIStructure.GPIO_Event = (uint8_t)0; //0 means falling edge, 1 raising

    GPIO_EXTIConfig(&GPIO_EXTIStructure);
  }
}

/**
 * @brief  To assert if the falling edge IRQ is enabled for that GPIO .
 * @param  xGpio Specifies the GPIO.
 *         This parameter can be one of following parameters:
 *         @arg M2S_GPIO_0: GPIO_0
 *         @arg M2S_GPIO_1: GPIO_1
 *         @arg M2S_GPIO_2: GPIO_2
 *         @arg M2S_GPIO_3: GPIO_3
 * @retval  Specifies the State.
 *         @arg ENABLE: Falling trigger is enabled
 *         @arg DISABLE: Falling trigger is disabled
 */
uint8_t S2LP_Middleware_GpioGetTriggerFalling(M2SGpioPin xGpio)
{
  uint32_t GPIO_Pin = s_vectnM2SGpioPin[xGpio];
  uint8_t edge = READ_BIT(GPIO->IS, GPIO_Pin) == 0;
  uint8_t both_edge = READ_BIT(GPIO->IBE, GPIO_Pin) == 1;
  uint8_t falling = READ_BIT(GPIO->IEV, GPIO_Pin) == 0;

  if (edge && !(both_edge))
    return falling ? 1 : 0;
  else
    return 0;
}

/**
 * @brief  Returns the level of a specified GPIO.
 * @param  xGpio Specifies the GPIO to be read.
 *         This parameter can be one of following parameters:
 *         @arg M2S_GPIO_0: GPIO_0
 *         @arg M2S_GPIO_1: GPIO_1
 *         @arg M2S_GPIO_2: GPIO_2
 *         @arg M2S_GPIO_3: GPIO_3
 * @retval Level of the GPIO. This parameter can be:
 *         1 or 0.
 */
uint8_t S2LP_Middleware_GpioGetLevel(M2SGpioPin xGpio)
{
  /* Gets the GPIO level */
  uint8_t ret;
  uint32_t GPIO_Pin = s_vectnM2SGpioPin[xGpio];

  ret = (uint8_t) GPIO_ReadBit(GPIO_Pin);

  return ret;
}

/**
 * @brief  Sets the level of a specified GPIO.
 * @param  xGpio Specifies the GPIO to be set.
 *         This parameter can be one of following parameters:
 *         @arg M2S_GPIO_0: GPIO_0
 *         @arg M2S_GPIO_1: GPIO_1
 *         @arg M2S_GPIO_2: GPIO_2
 *         @arg M2S_GPIO_3: GPIO_3
 *         @arg M2S_GPIO_SDN: SDN
 * @param  FlagStatus Level of the GPIO. This parameter can be:
 *         SET or RESET.
 * @retval None.
 */
void S2LP_Middleware_GpioSetLevel(M2SGpioPin xGpio, uint8_t level)
{
  BitAction xLevel = level ? Bit_SET : Bit_RESET;

  /* Sets the GPIO level */
  GPIO_WriteBit(s_vectnM2SGpioPin[xGpio], xLevel);}

/**
 * @brief  Gets the GPIO_PIN of the M2SGpioPin.
 * @param  xGpio: M2S GPIO.
 * @retval uint16_t GPIO_PIN value.
 */
uint32_t S2LP_Middleware_GpioGetPin(M2SGpioPin xGpio)
{
  return s_vectnM2SGpioPin[xGpio];
}

/** @defgroup S2LP_CORE_GPIO_Private_Functions	S2LP_CORE_GPIO Private Functions
 * @{
 */

void S2LPIRQInit(void)
{
  S2LP_Middleware_GpioInit((M2SGpioPin)S2LP_GPIO_IRQ_PIN, M2S_MODE_EXTI_IN);
}

void S2LPIRQEnable(uint8_t state, uint8_t edge_direction)
{
  S2LP_Middleware_GpioInit((M2SGpioPin)S2LP_GPIO_IRQ_PIN, M2S_MODE_EXTI_IN);
  S2LP_Middleware_GpioInterruptCmd((M2SGpioPin)S2LP_GPIO_IRQ_PIN, 0x00, 0x00, state, edge_direction);
}

void S2LPShutdownInit(void)
{
  GPIO_InitType GPIO_InitStructure;
  SysCtrl_PeripheralClockCmd(CLOCK_PERIPH_GPIO, ENABLE);

  GPIO_InitStructure.GPIO_Pin = S2LP_M2S_SDN_PIN;
  GPIO_InitStructure.GPIO_Mode = S2LP_M2S_SDN_MODE;
  GPIO_InitStructure.GPIO_Pull = S2LP_M2S_SDN_PUPD;
  GPIO_InitStructure.GPIO_HighPwr = S2LP_M2S_SDN_HIGH_POWER;
  GPIO_Init(&GPIO_InitStructure);

  S2LPShutdownEnter();
}

void S2LPShutdownEnter(void)
{
  /* Puts high the GPIO connected to shutdown pin */
  GPIO_SetBits(S2LP_M2S_SDN_PIN);
}

void S2LPShutdownExit(void)
{
  /* Puts low the GPIO connected to shutdown pin */
  GPIO_ResetBits(S2LP_M2S_SDN_PIN);

  /* Delay to allow the circuit POR */
  for(volatile uint32_t i=0;i<0x1E00;i++);
}

uint8_t S2LPShutdownCheck(void)
{
  return  (uint8_t) GPIO_ReadBit(S2LP_M2S_SDN_PIN);
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
