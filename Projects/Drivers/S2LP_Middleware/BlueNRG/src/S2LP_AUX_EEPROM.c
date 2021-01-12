/**
* @file    S2LP_AUX_EEPROM.c
* @author  LowPower RF BU - AMG
* @version 4.0.0
* @date    March, 2020
* @brief   S2LP AUX EEPROM management
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
#include "SDK_EVAL_Config.h"
#include "S2LP_AUX_EEPROM.h"
#include "S2LP_Middleware_Config.h"
#include <stdio.h>

/** @addtogroup S2LP_MIDDLEWARE_BLUENRG                     S2LP Middleware - BlueNRG
* @{
*/

/** @defgroup S2LP_AUX_EEPROM						S2LP AUX EEPROM
  * @brief  S2-LP EEPROM handling module.
  * This module exports all the main operations to deal with EEPROM.
  * @details See the file <i>@ref S2LP_AUX_EEPROM.h</i> for more details.
  * @{
*/


/**
* @brief  SPI buffer max size
*/
#define SPI_BUFF_SIZE                   (10)

/**
* @brief  SPI_TX DMA channel
*/
#define DMA_CH_SPI_TX                   (DMA_CH5)

/**
* @brief  SPI_TX DMA Transfer Complete Interrupt
*/
#define DMA_CH_SPI_TX_IT_TC             (DMA_FLAG_TC5)

/**
* @brief  SPI_RX DMA channel
*/
#define DMA_CH_SPI_RX                   (DMA_CH4)

/**
* @brief  SPI_RX DMA Transfer Complete Interrupt
*/
#define DMA_CH_SPI_RX_IT_TC             (DMA_FLAG_TC4)


/**
* @brief  SPI buffers used for DMA application
*/
static uint8_t spi_buffer_rx[128];
static uint8_t s_eeprom  = 0;


void EepromSpiInitialization(uint32_t baudrate)
{
  SPI_InitType SPI_InitStructure;
  GPIO_InitType GPIO_InitStructure;

  /* Enable SPI and GPIO clocks */
  SysCtrl_PeripheralClockCmd(CLOCK_PERIPH_GPIO | CLOCK_PERIPH_SPI, ENABLE);

  /* Configure SPI pins */
  GPIO_StructInit(&GPIO_InitStructure);
  GPIO_InitStructure.GPIO_Pin = EEPROM_SPI_MOSI_PIN;
  GPIO_InitStructure.GPIO_Mode = EEPROM_SPI_MOSI_MODE;
  GPIO_InitStructure.GPIO_Pull = EEPROM_SPI_MOSI_PUPD;
  GPIO_InitStructure.GPIO_HighPwr = EEPROM_SPI_MOSI_HIGH_POWER;
  GPIO_Init(&GPIO_InitStructure);

  GPIO_InitStructure.GPIO_Pin = EEPROM_SPI_MISO_PIN;
  GPIO_InitStructure.GPIO_Mode = EEPROM_SPI_MISO_MODE;
  GPIO_InitStructure.GPIO_Pull = EEPROM_SPI_MISO_PUPD;
  GPIO_InitStructure.GPIO_HighPwr = EEPROM_SPI_MISO_HIGH_POWER;
  GPIO_Init(&GPIO_InitStructure);

  GPIO_InitStructure.GPIO_Pin = EEPROM_SPI_MOSI_PIN;
  GPIO_InitStructure.GPIO_Mode = EEPROM_SPI_CLK_MODE;
  GPIO_InitStructure.GPIO_Pull = EEPROM_SPI_CLK_PUPD;
  GPIO_InitStructure.GPIO_HighPwr = EEPROM_SPI_CLK_HIGH_POWER;
  GPIO_Init(&GPIO_InitStructure);

  GPIO_InitStructure.GPIO_Pin = EEPROM_SPI_CS_PIN;
  GPIO_InitStructure.GPIO_Mode = EEPROM_SPI_CS_MODE;
  GPIO_InitStructure.GPIO_Pull = EEPROM_SPI_CS_PUPD;
  GPIO_InitStructure.GPIO_HighPwr = EEPROM_SPI_CS_HIGH_POWER;
  GPIO_Init(&GPIO_InitStructure);

  GPIO_SetBits(EEPROM_SPI_CS_PIN);

  /* Configure SPI in master mode */
  SPI_StructInit(&SPI_InitStructure);
  SPI_InitStructure.SPI_Mode = SPI_Mode_Master;
  SPI_InitStructure.SPI_DataSize = SPI_DataSize_8b ;
  SPI_InitStructure.SPI_CPOL = SPI_CPOL_Low;
  SPI_InitStructure.SPI_CPHA = SPI_CPHA_2Edge;
  SPI_InitStructure.SPI_BaudRate = baudrate;
  SPI_Init(&SPI_InitStructure);

  /* Clear RX and TX FIFO */
  SPI_ClearTXFIFO();
  SPI_ClearRXFIFO();

  /* Set null character */
  SPI_SetDummyCharacter(0xFF);

  /* Set communication mode */
  SPI_SetMasterCommunicationMode(SPI_FULL_DUPLEX_MODE);

  /* Configure DMA peripheral */
  SysCtrl_PeripheralClockCmd(CLOCK_PERIPH_DMA, ENABLE);

  DMA_InitType DMA_InitStructure;

  /* Configure DMA SPI TX channel */
  DMA_InitStructure.DMA_PeripheralBaseAddr = (uint32_t) &(SPI->DR);
  DMA_InitStructure.DMA_MemoryBaseAddr = (uint32_t)0;
  DMA_InitStructure.DMA_DIR = DMA_DIR_PeripheralDST;
  DMA_InitStructure.DMA_BufferSize = (uint32_t)SPI_BUFF_SIZE;
  DMA_InitStructure.DMA_PeripheralInc = DMA_PeripheralInc_Disable;
  DMA_InitStructure.DMA_MemoryInc = DMA_MemoryInc_Enable;
  DMA_InitStructure.DMA_PeripheralDataSize = DMA_PeripheralDataSize_Byte;
  DMA_InitStructure.DMA_MemoryDataSize = DMA_MemoryDataSize_Byte;
  DMA_InitStructure.DMA_Mode = DMA_Mode_Normal;
  DMA_InitStructure.DMA_Priority = DMA_Priority_Medium;
  DMA_InitStructure.DMA_M2M = DMA_M2M_Disable;
  DMA_Init(DMA_CH_SPI_TX, &DMA_InitStructure);

  /* Configure DMA SPI RX channel */
  DMA_InitStructure.DMA_MemoryBaseAddr = (uint32_t)0;
  DMA_InitStructure.DMA_BufferSize = (uint32_t)SPI_BUFF_SIZE;
  DMA_InitStructure.DMA_DIR = DMA_DIR_PeripheralSRC;
  DMA_InitStructure.DMA_Mode = DMA_Mode_Normal;
  DMA_Init(DMA_CH_SPI_RX, &DMA_InitStructure);
  //DMA_Cmd(DMA_CH_SPI_RX, ENABLE);

  /* Enable SPI_TX/SPI_RX DMA requests */
  SPI_DMACmd(SPI_DMAReq_Tx | SPI_DMAReq_Rx, ENABLE);

  /* Enable DMA_CH_UART_TX Transfer Complete interrupt */
  DMA_FlagConfig(DMA_CH_SPI_TX, DMA_FLAG_TC, ENABLE);
  DMA_FlagConfig(DMA_CH_SPI_RX, DMA_FLAG_TC, ENABLE);

}

void EepromCsPinInitialization(void)
{
  GPIO_InitType GPIO_InitStructure;

  /* Enable GPIO clock */
  SysCtrl_PeripheralClockCmd(CLOCK_PERIPH_GPIO, ENABLE);

  /* Configure EEPROM CS pin */
  GPIO_StructInit(&GPIO_InitStructure);

  GPIO_InitStructure.GPIO_Pin = EEPROM_SPI_CS_PIN;
  GPIO_InitStructure.GPIO_Mode = EEPROM_SPI_CS_MODE;
  GPIO_InitStructure.GPIO_Pull = EEPROM_SPI_CS_PUPD;
  GPIO_InitStructure.GPIO_HighPwr = EEPROM_SPI_CS_HIGH_POWER;
  GPIO_Init(&GPIO_InitStructure);

  GPIO_SetBits(EEPROM_SPI_CS_PIN);
}

uint8_t EepromRead(uint16_t nAddress, uint8_t cNbBytes, uint8_t* pcBuffer)
{
  uint8_t cmd[3], rxb[3];
  cmd[0] = EEPROM_CMD_READ; // READ HEADER

  for(uint8_t k=0; k<2; k++) {
    cmd[k+1] = (uint8_t)(nAddress>>((1-k)*8));
  }

  EepromCsPinInitialization();
  SpiRawTransaction(cmd, rxb, 3, pcBuffer, pcBuffer, cNbBytes, EEPROM_SPI_CS_PIN);

  return 0;
}

void EepromWaitEndWriteOperation(void)
{
  uint8_t status;

  /* Polling on status register */
  do
  {
    for(volatile uint32_t i=0;i<0x3ff;i++);
    status=EepromStatus();

  }while(status&EEPROM_STATUS_WIP);
}

void EepromWriteEnable(void)
{
  uint8_t rxb;
  uint8_t cmd = EEPROM_CMD_WREN;

  SpiRawTransaction(&cmd, &rxb, 1, NULL, NULL, 0, EEPROM_SPI_CS_PIN);
}

uint8_t EepromWrite(uint16_t nAddress, uint8_t cNbBytes, uint8_t* pcBuffer)
{
  uint8_t cmd[3];

  EepromCsPinInitialization();
  EepromWaitEndWriteOperation();

  /* SET the WREN flag */
  EepromWriteEnable();
  EepromWaitEndWriteOperation();

  cmd[0] = EEPROM_CMD_WRITE; /* Read Header */

  for(uint8_t k=0; k<2; k++) {
    cmd[k+1] = (uint8_t)(nAddress>>((1-k)*8)); }

  SpiRawTransaction(cmd, spi_buffer_rx, 3, pcBuffer, spi_buffer_rx, cNbBytes, EEPROM_SPI_CS_PIN);

  EepromWaitEndWriteOperation();

  return 0;
}

uint8_t EepromStatus(void)
{
  uint8_t cmd = EEPROM_CMD_RDSR;
  uint8_t status;

  SpiRawTransaction(&cmd, &status, 1, NULL, NULL, 0, EEPROM_SPI_CS_PIN);

  return status;
}

uint8_t EepromSetSrwd(void)
{
  uint8_t status;
  uint8_t cmd[] = {EEPROM_CMD_WRSR, EEPROM_STATUS_SRWD};

  /* Rearm the DMA_CH_SPI_TX */
  DMA_CH_SPI_TX->CMAR = (uint32_t)&cmd;
  DMA_CH_SPI_TX->CNDTR = 2;
  DMA_CH_SPI_RX->CMAR = (uint32_t)&status;
  DMA_CH_SPI_RX->CNDTR = 1;

  GPIO_ResetBits(EEPROM_SPI_CS_PIN);

  /* DMA_CH_SPI_TX enable */
  DMA_CH_SPI_TX->CCR_b.EN = SET;
  DMA_CH_SPI_RX->CCR_b.EN = SET;
  SPI_Cmd(ENABLE);

  while(!DMA_GetFlagStatus(DMA_CH_SPI_TX_IT_TC));
  DMA_ClearFlag(DMA_CH_SPI_TX_IT_TC);

  while(!DMA_GetFlagStatus(DMA_CH_SPI_RX_IT_TC));
  DMA_ClearFlag(DMA_CH_SPI_RX_IT_TC);

  GPIO_SetBits(EEPROM_SPI_CS_PIN);

  /* DMA_CH disable */
  DMA_CH_SPI_TX->CCR_b.EN = RESET;
  DMA_CH_SPI_RX->CCR_b.EN = RESET;
  while (SET == SPI_GetFlagStatus(SPI_FLAG_BSY));
  SPI_Cmd(DISABLE);

  return status;
}

uint8_t S2LPEvalGetHasEeprom(void)
{
  return s_eeprom;
}

void S2LPEvalSetHasEeprom(uint8_t eeprom)
{
#if EEPROM_PRESENT == EEPROM_YES
  s_eeprom = eeprom;
#else
  s_eeprom = 0;
#endif
}


/**
* @}
*/

/**
* @}
*/

/******************* (C) COPYRIGHT 2020 STMicroelectronics *****END OF FILE****/
