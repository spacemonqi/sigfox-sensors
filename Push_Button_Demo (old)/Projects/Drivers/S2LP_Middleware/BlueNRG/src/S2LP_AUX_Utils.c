/**
 * @file    S2LP_AUX_Utils.c
 * @author  LowPower RF BU - AMG
 * @version 4.0.0
 * @date    March, 2020
 * @brief   Identification functions for S2LP DK.
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
#include "SDK_UTILS_Timers.h"
#include "S2LP_Middleware_Config.h"
#include "S2LP_AUX_UTILS.h"
#include "S2LP_AUX_EEPROM.h"
#include "S2LP_CORE_GPIO.h"


/** @addtogroup S2LP_MIDDLEWARE_BLUENRG                           S2LP Middleware - BlueNRG
* @{
*/

/** @defgroup S2LP_AUX_UTILS						S2LP AUX UTILS
  * @brief  S2-LP Utils common module.
  * This module exports common functions for the middleware layer.
  * @{
*/

/**
* @brief This flag is used to synchronize the TIM3 ISR with the XtalMeasurement routine.
*/
static volatile uint8_t s_RfModuleBand = 0, s_Tcxo=0;
static volatile RangeExtType s_RfRangeExtender = RANGE_EXT_NONE;
static volatile uint32_t s_RfXtalFrequency = XTAL_FREQUENCY;
static volatile S2LPCutType s_S2LPCut = S2LP_CUT_2_1;

void S2LPRadioSetXtalFrequency(uint32_t lXtalFrequency);

RangeExtType S2LPManagementGetRangeExtender(void)
{
  return s_RfRangeExtender;
}

void S2LPManagementSetRangeExtender(RangeExtType value)
{
  s_RfRangeExtender = value;
}

void S2LPManagementSetBand(uint8_t band)
{
  s_RfModuleBand = band;
}

uint32_t S2LPGetFrequencyBand(void)
{
  uint32_t frequency = 0;
  const uint32_t band_frequencies[] = {
    169000000,
    315000000,
    433000000,
    868000000,
    915000000,
    450000000
  };

  if (s_RfModuleBand < (sizeof(band_frequencies)/sizeof(uint32_t))) {
    frequency = band_frequencies[s_RfModuleBand];
  }

  return frequency;
}

uint8_t S2LPManagementGetBand(void)
{
  return s_RfModuleBand;
}

uint32_t S2LPManagementComputeXtalFrequency(void)
{
  s_RfXtalFrequency=50000000;
  return s_RfXtalFrequency;
}

uint32_t S2LPManagementGetXtalFrequency(void)
{
  return s_RfXtalFrequency;
}

uint8_t S2LPManagementGetTcxo(void)
{
  return s_Tcxo;
}

__weak void S2LPRadioSetXtalFrequency(uint32_t xtal)
{
  s_RfXtalFrequency = xtal;
}

S2LPCutType S2LPManagementGetCut(void)
{
  return s_S2LPCut;
}

void S2LPManagementIdentificationRFBoard(void)
{
  uint8_t tmp;

  /* Read Cut version from S2LP register */
  S2LPSpiReadRegisters(0xF1, 1, &tmp);
  s_S2LPCut = (S2LPCutType)tmp;

#if EEPROM_PRESENT == EEPROM_YES
  uint8_t was_in_sdn=1;
  int32_t xtal_comp_value;

  if(S2LPShutdownCheck()==RESET)
  {
    /* if reset it was not in SDN */
    S2LPShutdownEnter();
    was_in_sdn=0;
  }

  EepromIdentification();

  /* Read the EEPROM */
  uint8_t tmpBuffer[32];
  EepromRead(0x0000, 32, tmpBuffer);

  float foffset=0;
  if(tmpBuffer[0]==0 || tmpBuffer[0]==0xFF) {
    S2LPManagementComputeXtalFrequency();
    if(was_in_sdn==0) { S2LPShutdownExit(); }

    /* If EEPROM fails, set no EXT_PA by default */
    S2LPManagementSetRangeExtender(RANGE_EXT_NONE);

    return;
  }
  switch(tmpBuffer[1]) {
  case 0:
    s_RfXtalFrequency = 24000000;
    break;
  case 1:
    s_RfXtalFrequency = 25000000;
    break;
  case 2:
    s_RfXtalFrequency = 26000000;
    break;
  case 3:
    s_RfXtalFrequency = 48000000;
    break;
  case 4:
    s_RfXtalFrequency = 50000000;
    break;
  case 5:
    s_RfXtalFrequency = 52000000;
    break;
  default:
    s_RfXtalFrequency=S2LPManagementComputeXtalFrequency();

    break;
  }

  s_RfModuleBand=tmpBuffer[3];

  EepromRead(0x0021,4,tmpBuffer);
  for(uint8_t i=0;i<4;i++)
  {
    ((uint8_t*)&foffset)[i]=tmpBuffer[3-i];
  }

  xtal_comp_value = 0;

  /* foffset is a value measured during manufacturing as follows:
  foffset=fnominal-fmeasured. To compensate such value it should
  be reported to xtal freq and then subtracted */
  if (foffset != 0xFFFFFFFF) {
    uint32_t frequency = S2LPGetFrequencyBand();

    if (frequency != 0) {
	uint32_t xtal_frequency = s_RfXtalFrequency;

	/* This is the value to be added to the xtal nominal value
	to compensate the xtal offset*/
	xtal_comp_value = (int32_t) ((xtal_frequency*(-foffset))/frequency);
    }
  }

  S2LPRadioSetXtalFrequency(s_RfXtalFrequency+xtal_comp_value);

  S2LPManagementSetRangeExtender((RangeExtType)tmpBuffer[5]);

  if(was_in_sdn==0)
  {
    S2LPShutdownExit();
  }
#endif
}

uint8_t EepromIdentification(void)
{
  uint8_t status=0;

  /* Configure EEPROM SPI with default configuration */
  EepromSpiInitialization(8000000);
  EepromCsPinInitialization();

  return status;
}

void S2LPManagementRcoCalibration(void)
{
  uint8_t tmp[2], tmp2;

  S2LPSpiReadRegisters(0x6D, 1, &tmp2);
  tmp2 |= 0x01;
  S2LPSpiWriteRegisters(0x6D, 1, &tmp2);

  S2LPSpiCommandStrobes(0x63);
  SdkDelayMs(100);
  S2LPSpiCommandStrobes(0x62);

  do
  {
    S2LPSpiReadRegisters(0x8D, 1, tmp);
  }
  while((tmp[0]&0x10)==0);

  S2LPSpiReadRegisters(0x94, 2, tmp);
  S2LPSpiReadRegisters(0x6F, 1, &tmp2);
  tmp[1]=(tmp[1]&0x80)|(tmp2&0x7F);

  S2LPSpiWriteRegisters(0x6E, 2, tmp);
  S2LPSpiReadRegisters(0x6D, 1, &tmp2);
  tmp2 &= 0xFE;

  S2LPSpiWriteRegisters(0x6D, 1, &tmp2);
}

/**
* @}
*/

/**
* @}
*/

/******************* (C) COPYRIGHT 2020 STMicroelectronics *****END OF FILE****/
