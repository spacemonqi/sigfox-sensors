#include "ST_Init.h"
#include "sigfox_stack.h"

int ST_Init(void)
{
  int nRet = 0;

  /* System initialization function */
  SystemInit();

  /* System clock initialization */
  Clock_Init();

  /* Enable the GPIO Clock */
  SysCtrl_PeripheralClockCmd(CLOCK_PERIPH_GPIO | CLOCK_PERIPH_SPI, ENABLE);

  /* Put the radio off */
  S2LPShutdownInit();
  SdkDelayMs(10);
  S2LPShutdownExit();

  /* SPI init */
  S2LPSpiInit(8000000);

  /* Set the EEPROM availability */
  S2LPEvalSetHasEeprom(EEPROM_PRESENT);

  /* Auto detect settings, if EEPROM is available */
#if EEPROM_PRESENT == EEPROM_YES
  /*  Set EEPROM CS */
  EepromCsPinInitialization();

  /* Identify the S2-LP RF board reading some production data */
  S2LPManagementIdentificationRFBoard();
#elif EEPROM_PRESENT==EEPROM_NO
  /* Set XTAL frequency with offset */
  S2LPRadioSetXtalFrequency(XTAL_FREQUENCY+XTAL_FREQUENCY_OFFSET);

  /* Set the frequency base */
  S2LPManagementSetBand(BOARD_FREQUENCY_BAND);

  /* Configure PA availability */
  S2LPManagementSetRangeExtender(DetetctPA());
#endif

  if(!nRet)
  {
    /* uC IRQ config and enable */
    S2LPIRQInit();
    S2LPIRQEnable(ENABLE, M2S_GPIO_EDGE_EVENT);

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
  SdkEvalPushButtonInit(BUTTON_2);

  if(!SdkEvalPushButtonGetState(BUTTON_2))
    nBtnPressed = 1;

  return nBtnPressed;
}

void ButtonSetIRQ(void)
{
  SdkEvalPushButtonIrq(BUTTON_2, IRQ_ON_RISING_EDGE);
}

uint8_t IsButtonPressed(void)
{
  return SdkEvalPushButtonGetState(BUTTON_2);
}

RangeExtType DetetctPA(void)
{
#if S2LP_FEM_PRESENT == S2LP_FEM_NO
  	return RANGE_EXT_NONE;
#else
#ifdef MON_REF_DES
	return RANGE_EXT_SKYWORKS_SKY66420;
#else
	return RANGE_EXT_SKYWORKS_SE2435L;
#endif
#endif
}

