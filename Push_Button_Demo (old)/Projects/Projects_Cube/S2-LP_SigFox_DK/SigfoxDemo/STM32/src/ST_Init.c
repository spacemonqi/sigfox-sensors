#include "ST_Init.h"
#include "sigfox_types.h"
#include "sigfox_api.h"
#include "st_rf_api.h"
#include "st_mcu_api.h"


int ST_Init(void)
{
  int nRet = 0;

  /* System initialization function */
  HAL_Init();

  /* System clock initialization */
  ST_MCU_API_SetSysClock();

  /* Put the radio off */
  S2LPShutdownInit();
  SdkDelayMs(10);
  S2LPShutdownExit();

  /* SPI init */
  S2LPSpiInit();

  /* Set the EEPROM availability */
  S2LPEvalSetHasEeprom(EEPROM_PRESENT);

  /* Auto detect settings, if EEPROM is available */
#if EEPROM_PRESENT == EEPROM_YES
  /* Identify the S2-LP RF board reading some production data */
  S2LPManagementIdentificationRFBoard();
#elif EEPROM_PRESENT==EEPROM_NO
  /* Set XTAL frequency with offset */
  S2LPRadioSetXtalFrequency(XTAL_FREQUENCY+XTAL_FREQUENCY_OFFSET);

  /* Set the frequency base */
  S2LPManagementSetBand(BOARD_FREQUENCY_BAND);

  /* Configure PA availability */
#if S2LP_FEM_PRESENT == S2LP_FEM_NO
  S2LPManagementSetRangeExtender(0);
#else
  S2LPManagementSetRangeExtender(1);
#endif
#endif

  if(!nRet)
  {
    /* uC IRQ config and enable */
    S2LPIRQInit();
    S2LPIRQEnable(ENABLE, S2LP_GPIO_IRQ_EDGE_EVENT);

    /* FEM Initialization */
    FEM_Init();

    /* TCXO Initialization */
    TCXO_Init();
  }

  return nRet;
}

uint8_t ButtonInit(void)
{
  int nBtnPressed = 0;
  SdkEvalPushButtonInit(BUTTON_1);

  if(!SdkEvalPushButtonGetState(BUTTON_1))
    nBtnPressed = 1;

  return nBtnPressed;
}

void ButtonSetIRQ(void)
{
  SdkEvalPushButtonIrq(BUTTON_1, BUTTON_MODE_EXTI);
}

uint8_t IsButtonPressed(void)
{
  return SdkEvalPushButtonGetState(BUTTON_1);
}

void ST_MANUF_report_CB(uint8_t status, int32_t rssi){}
