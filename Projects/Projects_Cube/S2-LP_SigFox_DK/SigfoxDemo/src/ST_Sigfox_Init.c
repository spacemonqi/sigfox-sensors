#include "ST_Sigfox_Init.h"
#include "SDK_UTILS_Flash.h"
#include "SDK_UTILS_Timers.h"


ST_SFX_ERR St_Sigfox_Open_RCZ(uint8_t rcz)
{
  ST_SFX_ERR open_err = ST_SFX_ERR_NONE;

  switch(rcz)
  {
    case 1:
      {
        /* Turn PA off in RC1/3/5/6/7 */
        ST_RF_API_set_pa(0);
        /* RC1 - open the Sigfox library */
        if(SIGFOX_API_open(&(sfx_rc_t)RC1)!=0)
        {
          /* Stuck in case of error */
          open_err = ST_SFX_ERR_OPEN;
        }
        break;
      }
    case 2:
      {
        /* Turn PA off in RC2 and RC4 */
        ST_RF_API_set_pa(1);
        /* RC2 - open the Sigfox library */
        if(SIGFOX_API_open(&(sfx_rc_t)RC2)!=0)
        {
          /* Stuck in case of error */
          open_err = ST_SFX_ERR_OPEN;
        }

        /* In FCC we can choose the macro channel to use by a 86 bits bitmask
        In this case we use the first 9 macro channels */
        sfx_u32 config_words[3]=RC2_SM_CONFIG;

        /* Set the standard configuration with default channel to 1 */
        if(SIGFOX_API_set_std_config(config_words,0)!=0)
        {
          /* Stuck in case of error */
          open_err = ST_SFX_ERR_OPEN;
        }
        break;
      }
    case 3:
      {
        volatile uint8_t ret;
        /* Turn PA off in RC1/3/5/6/7 */
        ST_RF_API_set_pa(0);
        ret=SIGFOX_API_open(&(sfx_rc_t)RC3C);
        /* RC3 - open the Sigfox library */
        if(ret!=0)
        {
          /* Stuck in case of error */
          open_err = ST_SFX_ERR_OPEN;
        }

        /* In FCC we can choose the macro channel to use by a 86 bits bitmask
        In this case we use 9 consecutive macro channels starting from 63 (920.8MHz) */
        sfx_u32 config_words[3]=RC3C_CONFIG;

        /* Set the standard configuration with default channel to 63 */
        if(SIGFOX_API_set_std_config(config_words,0)!=0)
        {
          /* Stuck in case of error */
          open_err = ST_SFX_ERR_OPEN;
        }
        break;
      }
    case 4:
      {
        volatile uint8_t ret;
        /* Turn PA off in RC2 and RC4 */
        ST_RF_API_set_pa(1);

        ret=SIGFOX_API_open(&(sfx_rc_t)RC4);
        /* RC4 - open the Sigfox library */
        if(ret!=0)
        {
          /* Stuck in case of error */
          open_err = ST_SFX_ERR_OPEN;
        }

        /* In FCC we can choose the macro channel to use by a 86 bits bitmask
        In this case we use 9 consecutive macro channels starting from 63 (920.8MHz) */
        sfx_u32 config_words[3]=RC4_SM_CONFIG;

        /* Set the standard configuration with default channel to 63 */
        if(SIGFOX_API_set_std_config(config_words,1)!=0)
        {
          /* Stuck in case of error */
          open_err = ST_SFX_ERR_OPEN;
        }
        break;
      }
    case 5:
      {
        volatile uint8_t ret;
        /* Turn PA off in RC1/3/5/6/7 */
        ST_RF_API_set_pa(0);
        ret=SIGFOX_API_open(&(sfx_rc_t)RC5);
        /* RC5 - open the Sigfox library */
        if(ret!=0)
        {
          /* Stuck in case of error */
          open_err = ST_SFX_ERR_OPEN;
        }

        /* In FCC we can choose the macro channel to use by a 86 bits bitmask
        In this case we use 9 consecutive macro channels starting from 63 (920.8MHz) */
        sfx_u32 config_words[3]=RC5_CONFIG;

        /* Set the standard configuration with default channel to 63 */
        if(SIGFOX_API_set_std_config(config_words,0)!=0)
        {
          /* Stuck in case of error */
          open_err = ST_SFX_ERR_OPEN;
        }
        break;
      }
    case 6:
      {
        /* Turn PA off in RC1/3/5/6/7 */
        ST_RF_API_set_pa(0);
        /* RC6 - open the Sigfox library */
        if(SIGFOX_API_open(&(sfx_rc_t)RC6)!=0)
        {
          /* Stuck in case of error */
          open_err = ST_SFX_ERR_OPEN;
        }
        break;
      }
    case 7:
      {
        /* Turn PA off in RC1/3/5/6/7 */
        ST_RF_API_set_pa(0);
        /* RC7 - open the Sigfox library */
        if(SIGFOX_API_open(&(sfx_rc_t)RC7)!=0)
        {
          /* Stuck in case of error */
          open_err = ST_SFX_ERR_OPEN;
        }
        break;
      }
    default:
      {
        /* Stuck the application for a out of range number */
        open_err = ST_SFX_ERR_RC_UNKNOWN;
        break;
      }
    }
  return open_err;
}

ST_SFX_ERR ST_Sigfox_Init(NVM_BoardDataType *sfxConfig, uint8_t openAfterInit)
{
  ST_SFX_ERR ret_err = ST_SFX_ERR_NONE;

  /* Configure XTAL frequency and offset for the RF Library */
  ST_RF_API_set_xtal_freq(S2LPManagementGetXtalFrequency());

  /* Macro that defines and initializes the nvmconfig structure */
  INIT_NVM_CONFIG(nvmConfig);

  /* Sigfox Credentials Management */
#ifdef USE_FLASH
  nvmConfig.nvmType = NVM_TYPE_FLASH;
  nvmConfig.sfxDataAddress = (uint32_t)FLASH_USER_START_ADDR;	/* Set here the address for 'NVM sigfox data' management */
  nvmConfig.boardDataAddress = (uint32_t)FLASH_BOARD_START_ADDR;	/* Set here the address for 'NVM board data' management */
#endif

  /* Configure the NVM_API */
  SetNVMInitial(&nvmConfig);

#ifdef USE_FLASH
  /* Retrieve Sigfox info from FLASH */
  if(enc_utils_retrieve_data_from_flash(sfxConfig, UID_ADDRESS, UID_LEN) != 0)
  	ret_err = ST_SFX_ERR_CREDENTIALS;

  if(!ret_err)
  {
    ret_err = (ST_SFX_ERR)ST_RF_API_set_xtal_freq(S2LPManagementGetXtalFrequency()+sfxConfig->freqOffset);  /* Override RF_API Xtal value */

    if(!ret_err)
      ret_err = (ST_SFX_ERR)ST_RF_API_set_rssi_offset(sfxConfig->rssiOffset); /* Override RSSI offset */

    if(!ret_err)
    	ret_err = (ST_SFX_ERR)ST_RF_API_set_lbt_thr_offset(sfxConfig->lbtOffset); /* Override LBT threshold offset */

    if(ret_err) /* An error occured reading freq, RSSI or LBT offsets */
	ret_err = ST_SFX_ERR_OFFSET;
  }
#else
  /* Retrieve Sigfox info from EEPROM */
  if(enc_utils_retrieve_data(&sfxConfig->id, sfxConfig->pac, &sfxConfig->rcz) != 0)
  	ret_err = ST_SFX_ERR_CREDENTIALS;
  else
    sfxConfig->freqOffset = S2LPManagementGetXtalFrequency();
#endif

  /* If the retriever returns an error (code different from ST_SFX_ERR_NONE) the application will halt */
  /* Otherwise, open the Sigfox Library according to the zone stored in the device */
  if(openAfterInit && ret_err == ST_SFX_ERR_NONE)
    ret_err = St_Sigfox_Open_RCZ(sfxConfig->rcz);

  return ret_err;
}

void ST_Sigfox_SetPublicKey(uint8_t en)
{
  enc_utils_set_public_key(en);
}
