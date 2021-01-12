/**
 * @file    S2LP_CORE_SPI.c
 * @author  LowPower RF BU - AMG
 * @version 2.1.1
 * @date    May, 2020
 * @brief   This file provides all the low level API to manage SPI interface for eval board.
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
#include "S2LP_CORE_SPI.h"
#include "SDK_EVAL_Config.h"
#include "S2LP_Middleware_Config.h"
#include <stdio.h>

/** @addtogroup S2LP_CORE_BLUENRG                     S2LP CORE - BlueNRG
* @{
*/

/** @defgroup S2LP_CORE_SPI					S2LP CORE SPI
  * @brief  S2-LP SPI handling module.
  * This module exports all the main operations to deal with SPI.
  * @details See the file <i>@ref S2LP_CORE_SPI.h</i> for more details.
  * @{
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

#define SPI_BUFF_SIZE                   (10)


#define DELAY_CS_SCLK			0x70	/* Patch EMEA 2019-11-08 : Delay between CSn falling edge & start of SCLK, must be tuned.*/
#define DELAY_BEFORE_DATA_READ	0x70	/* Patch EMEA 2019-11-08 : Delay before the read of SPI data, must be tuned.*/

#define M2S_SPI_GPIO_NUMBER 		4

#define LINEAR_FIFO_ADDRESS		0xFF  /*!< Linear FIFO address*/
#define RSSI_LEVEL_RUN_ADDRESS	0xEF	/*!< RSSI RUN Register address*/

/** @defgroup S2LP_CORE_SPI_Functions			S2LP CORE SPI exported functions
* @{
*/

/**
 * @brief  SPI buffers used for DMA application
 */
static uint8_t spi_buffer_tx[130];
static uint8_t spi_buffer_rx[130];
static volatile uint8_t spi_in_use=0;

__weak void S2LPSpiRawTc(void){}

/**
 * @defgroup S2LP_EVAL_SPI_Public_Functions                S2LP EVAL SPI Public Functions
 * @{
 */
void S2LPSpiInit(uint32_t baudrate)
{
  SPI_InitType SPI_InitStructure;
  GPIO_InitType GPIO_InitStructure;

  /* Enable SPI and GPIO clocks */
  SysCtrl_PeripheralClockCmd(CLOCK_PERIPH_GPIO | CLOCK_PERIPH_SPI, ENABLE);

  /* Configure SPI pins */
  GPIO_StructInit(&GPIO_InitStructure);
  GPIO_InitStructure.GPIO_Pin = S2LP_SPI_MOSI_PIN;
  GPIO_InitStructure.GPIO_Mode = S2LP_SPI_MOSI_MODE;
  GPIO_InitStructure.GPIO_Pull = S2LP_SPI_MOSI_PUPD;
  GPIO_InitStructure.GPIO_HighPwr = S2LP_SPI_MOSI_HIGH_POWER;
  GPIO_Init(&GPIO_InitStructure);

  GPIO_InitStructure.GPIO_Pin = S2LP_SPI_MISO_PIN;
  GPIO_InitStructure.GPIO_Mode = S2LP_SPI_MISO_MODE;
  GPIO_InitStructure.GPIO_Pull = S2LP_SPI_MISO_PUPD;
  GPIO_InitStructure.GPIO_HighPwr = S2LP_SPI_MISO_HIGH_POWER;
  GPIO_Init(&GPIO_InitStructure);

  GPIO_InitStructure.GPIO_Pin = S2LP_SPI_CLK_PIN;
  GPIO_InitStructure.GPIO_Mode = S2LP_SPI_CLK_MODE;
  GPIO_InitStructure.GPIO_Pull = S2LP_SPI_CLK_PUPD;
  GPIO_InitStructure.GPIO_HighPwr = S2LP_SPI_CLK_HIGH_POWER;
  GPIO_Init(&GPIO_InitStructure);

  GPIO_InitStructure.GPIO_Pin = S2LP_SPI_CS_PIN;
  GPIO_InitStructure.GPIO_Mode = S2LP_SPI_CS_MODE;
  GPIO_InitStructure.GPIO_Pull = S2LP_SPI_CS_PUPD;
  GPIO_InitStructure.GPIO_HighPwr = S2LP_SPI_CS_HIGH_POWER;
  GPIO_Init(&GPIO_InitStructure);

  GPIO_SetBits(S2LP_SPI_CS_PIN);

  SPI_DeInit();

  /* Configure SPI in master mode */
  SPI_StructInit(&SPI_InitStructure);
  SPI_InitStructure.SPI_Mode = SPI_Mode_Master;
  SPI_InitStructure.SPI_DataSize = SPI_DataSize_8b;
  SPI_InitStructure.SPI_CPOL = SPI_CPOL_Low;
  SPI_InitStructure.SPI_CPHA = SPI_CPHA_1Edge;//SPI_CPHA_2Edge;
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
  DMA_InitStructure.DMA_PeripheralBaseAddr = SPI_DR_BASE_ADDR;
  DMA_InitStructure.DMA_MemoryBaseAddr = (uint32_t)spi_buffer_tx;
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
  DMA_InitStructure.DMA_MemoryBaseAddr = (uint32_t)spi_buffer_rx;
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

/**
* @brief  Deinitializes the SPI.
* @param  None
* @retval None
*/
__weak void SdkEvalSpiDeinit(void) { }

void SpiRawTransaction(uint8_t *tx_buffer, uint8_t *rx_buffer, uint16_t length,
			     uint8_t *tx_buffer2, uint8_t *rx_buffer2, uint16_t length2,
			     uint32_t cs)
{
  /* Rearm the DMA_CH_SPI_TX */
  DMA_CH_SPI_TX->CMAR = (uint32_t)tx_buffer;
  DMA_CH_SPI_TX->CNDTR = length;
  DMA_CH_SPI_RX->CMAR = (uint32_t)rx_buffer;
  DMA_CH_SPI_RX->CNDTR = length;

  GPIO_ResetBits(cs);
  for(volatile uint32_t i=0;i<DELAY_CS_SCLK;i++);

  /* DMA_CH_SPI_TX enable */
  DMA_CH_SPI_TX->CCR_b.EN = SET;
  DMA_CH_SPI_RX->CCR_b.EN = SET;
  SPI_Cmd(ENABLE);

  while(!DMA_GetFlagStatus(DMA_CH_SPI_TX_IT_TC));
  DMA_ClearFlag(DMA_CH_SPI_TX_IT_TC);

  while(!DMA_GetFlagStatus(DMA_CH_SPI_RX_IT_TC));
  DMA_ClearFlag(DMA_CH_SPI_RX_IT_TC);

  /* DMA1 finished the transfer of SrcBuffer */

  /* DMA_CH disable */
  DMA_CH_SPI_TX->CCR_b.EN = RESET;
  DMA_CH_SPI_RX->CCR_b.EN = RESET;

  while (SET == SPI_GetFlagStatus(SPI_FLAG_BSY));

  for(volatile uint32_t i=0;i<DELAY_BEFORE_DATA_READ;i++);  //Patch EMEA : Delay added in STANDBY mode.

  if(tx_buffer2 != NULL && rx_buffer2 != NULL)
  {
    /* Rearm the DMA_CH_SPI_TX */
    DMA_CH_SPI_TX->CMAR = (uint32_t)tx_buffer2;
    DMA_CH_SPI_TX->CNDTR = length2;
    DMA_CH_SPI_RX->CMAR = (uint32_t)rx_buffer2;
    DMA_CH_SPI_RX->CNDTR = length2;

    /* DMA_CH_SPI_TX enable */
    DMA_CH_SPI_TX->CCR_b.EN = SET;
    DMA_CH_SPI_RX->CCR_b.EN = SET;

    while(!DMA_GetFlagStatus(DMA_CH_SPI_RX_IT_TC));
    DMA_ClearFlag(DMA_CH_SPI_RX_IT_TC);
  }

  for(volatile uint32_t i=0;i<DELAY_CS_SCLK;i++);

  /* DMA1 finished the transfer of SrcBuffer */
  GPIO_SetBits(cs);

  /* DMA_CH disable */
  DMA_CH_SPI_TX->CCR_b.EN = RESET;
  DMA_CH_SPI_RX->CCR_b.EN = RESET;

  while (SET == SPI_GetFlagStatus(SPI_FLAG_BSY));

  SPI_Cmd(DISABLE);

  S2LPSpiRawTc();
}

uint16_t S2LPSpiReadRegisters(uint8_t address, uint8_t n_bytes, uint8_t* buffer)
{
  uint16_t status;
  uint8_t *status_b=(uint8_t*)&status;
  uint8_t cmd[2];
  cmd[0]=0x01;          /* READ register header */
  cmd[1]=address;       /* ADDRESS of the register to read */

  (*status_b)=0;

  SpiRawTransaction(cmd, status_b, 2, spi_buffer_tx, buffer, n_bytes, S2LP_SPI_CS_PIN);

  cmd[0]=status_b[1];
  status_b[1]=status_b[0];
  status_b[0]=cmd[0];

  return status;
}

uint16_t S2LPSpiWriteRegisters(uint8_t address, uint8_t n_bytes, uint8_t* buffer)
{
  uint16_t status;
  uint8_t *status_b=(uint8_t*)&status;
  uint8_t cmd[2];
  cmd[0]=0x00;       /* WRITE register header */
  cmd[1]=address;    /* ADDRESS of the register to write */

  (*status_b)=0;

  SpiRawTransaction(cmd, status_b, 2, buffer, spi_buffer_rx, n_bytes, S2LP_SPI_CS_PIN);

  cmd[0]=status_b[1];
  status_b[1]=status_b[0];
  status_b[0]=cmd[0];

  return status;
}

uint16_t S2LPSpiCommandStrobes(uint8_t command)
{
  uint16_t status;
  uint8_t *status_b=(uint8_t*)&status;
  uint8_t cmd[2];
  cmd[0]=0x80;//cmd register header
  cmd[1]=command;

  (*status_b)=0;

  SpiRawTransaction(cmd, status_b, 2, NULL, NULL, 0, S2LP_SPI_CS_PIN);

  cmd[0]=status_b[1];
  status_b[1]=status_b[0];
  status_b[0]=cmd[0];
  return status;
}

uint16_t S2LPSpiReadFifo(uint8_t n_bytes, uint8_t* buffer)
{
  uint16_t status;
  uint8_t *status_b=(uint8_t*)&status;
  uint8_t cmd[2];
  cmd[0]=0x01; //READ register header
  cmd[1]=LINEAR_FIFO_ADDRESS;

  (*status_b)=0;

  SpiRawTransaction(cmd, status_b, 2, buffer, buffer, n_bytes, S2LP_SPI_CS_PIN);

  cmd[0]=status_b[1];
  status_b[1]=status_b[0];
  status_b[0]=cmd[0];

  return status;
}

uint16_t S2LPSpiWriteFifo(uint8_t n_bytes, uint8_t* buffer)
{
  uint16_t status;
  uint8_t *status_b=(uint8_t*)&status;
  uint8_t cmd[2];
  cmd[0]=0x00; //WRITE register header
  cmd[1]=LINEAR_FIFO_ADDRESS;

  (*status_b)=0;

  SpiRawTransaction(cmd, status_b, 2, buffer, spi_buffer_rx, n_bytes, S2LP_SPI_CS_PIN);

  cmd[0]=status_b[1];
  status_b[1]=status_b[0];
  status_b[0]=cmd[0];

  return status;
}

void S2LPSetSpiInUse(uint8_t state)
{
  spi_in_use = state;
}

uint8_t S2LPGetSpiInUse()
{
  return spi_in_use;
}

void S2LPSpiRaw(uint8_t n_bytes, uint8_t* in_buffer, uint8_t* out_buffer, uint8_t can_return_bef_tx)
{
  DMA_ClearFlag(DMA_CH_SPI_RX_IT_TC);
  DMA_ClearFlag(DMA_CH_SPI_TX_IT_TC);

  /* Rearm the DMA_CH_SPI_TX */
  DMA_CH_SPI_TX->CMAR = (uint32_t)in_buffer;
  DMA_CH_SPI_TX->CNDTR = n_bytes;
  if(out_buffer!=NULL)
  {
    DMA_CH_SPI_RX->CMAR = (uint32_t)out_buffer;
  }
  else
  {
    DMA_CH_SPI_RX->CMAR = (uint32_t)spi_buffer_rx;
  }
  DMA_CH_SPI_RX->CNDTR = n_bytes;

  if(can_return_bef_tx)
  {
    NVIC_Init(&(NVIC_InitType){DMA_IRQn,MED_PRIORITY,ENABLE});
  }
  else
  {
    NVIC_Init(&(NVIC_InitType){DMA_IRQn,MED_PRIORITY,DISABLE});
  }

  GPIO_ResetBits(S2LP_SPI_CS_PIN);
  for(volatile uint32_t i=0;i<DELAY_CS_SCLK;i++);

  /* DMA_CH_SPI_TX enable */
  DMA_CH_SPI_RX->CCR_b.EN = SET;
  DMA_CH_SPI_TX->CCR_b.EN = SET;
  SPI_Cmd(ENABLE);

  if(!can_return_bef_tx)
  {
    while(!DMA_GetFlagStatus(DMA_CH_SPI_RX_IT_TC));
    DMA_ClearFlag(DMA_CH_SPI_RX_IT_TC);

    /* DMA_CH disable */
    DMA_CH_SPI_TX->CCR_b.EN = RESET;
    DMA_CH_SPI_RX->CCR_b.EN = RESET;
    while (SET == SPI_GetFlagStatus(SPI_FLAG_BSY));

    for(volatile uint32_t i=0;i<DELAY_CS_SCLK;i++);
    GPIO_SetBits(S2LP_SPI_CS_PIN);

    SPI_Cmd(DISABLE);

    S2LPSpiRawTc();
  }
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
