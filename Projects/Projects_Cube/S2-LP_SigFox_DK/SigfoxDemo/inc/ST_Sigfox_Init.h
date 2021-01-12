#include "S2LP_Middleware_Config.h"
#include "SDK_EVAL_Config.h"
#include "sigfox_stack.h"

typedef enum {
  ST_SFX_ERR_NONE = 0,
  ST_SFX_ERR_OPEN = 1,
  ST_SFX_ERR_CREDENTIALS = 2,
  ST_SFX_ERR_OFFSET = 3,
  ST_SFX_ERR_RC_UNKNOWN = 99
} ST_SFX_ERR;


/**
 * @brief  Opens Sigfox Library according to the zone.
 * @param rcz The Radio Zone
 * @retval Returns 0 if ok.
 */
ST_SFX_ERR St_Sigfox_Open_RCZ(uint8_t rcz);


/**
 * @brief  Sigfox subsystem main initialization.
 * @param  openAfterInit if 1 opens the library after the initialization process
 * @retval error code
 */
ST_SFX_ERR ST_Sigfox_Init(NVM_BoardDataType *sfxConfig, uint8_t openAfterInit);


/**
 * @brief  Function to set or not the device in Public Key mode
 * @param  en Set this flag to 1 to enable Public Key mode. 0 otherwise.
 * @retval None
 */
void ST_Sigfox_SetPublicKey(uint8_t en);

