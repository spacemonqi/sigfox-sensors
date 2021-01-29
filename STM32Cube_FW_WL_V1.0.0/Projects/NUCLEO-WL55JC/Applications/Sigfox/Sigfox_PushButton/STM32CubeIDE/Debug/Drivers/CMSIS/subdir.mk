################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
C:/Users/name/Desktop/STM32Cube_FW_WL_V1.0.0/Current/STM32Cube_FW_WL_V1.0.0/Projects/NUCLEO-WL55JC/Applications/Sigfox/Sigfox_PushButton/Core/Src/system_stm32wlxx.c 

OBJS += \
./Drivers/CMSIS/system_stm32wlxx.o 

C_DEPS += \
./Drivers/CMSIS/system_stm32wlxx.d 


# Each subdirectory must supply rules for building sources it contributes
Drivers/CMSIS/system_stm32wlxx.o: C:/Users/name/Desktop/STM32Cube_FW_WL_V1.0.0/Current/STM32Cube_FW_WL_V1.0.0/Projects/NUCLEO-WL55JC/Applications/Sigfox/Sigfox_PushButton/Core/Src/system_stm32wlxx.c
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DUSE_HAL_DRIVER -DSTM32WL55xx -DCORE_CM4 -DDEBUG -c -I../../Core/Inc -I../../Sigfox/App -I../../Sigfox/Target -I../../../../../../../Drivers/STM32WLxx_HAL_Driver/Inc -I../../../../../../../Drivers/CMSIS/Include -I../../../../../../../Drivers/CMSIS/Device/ST/STM32WLxx/Include -I../../../../../../../Middlewares/Third_Party/Sigfox/Crypto -I../../../../../../../Middlewares/Third_Party/Sigfox/Monarch -I../../../../../../../Middlewares/Third_Party/Sigfox/SigfoxLib -I../../../../../../../Middlewares/Third_Party/Sigfox/SigfoxLibTest -I../../../../../../../Middlewares/Third_Party/SubGHz_Phy -I../../../../../../../Middlewares/Third_Party/SubGHz_Phy/stm32_radio_driver -I../../../../../../../Utilities/lpm/tiny_lpm -I../../../../../../../Utilities/misc -I../../../../../../../Utilities/sequencer -I../../../../../../../Utilities/timer -I../../../../../../../Utilities/trace/adv_trace -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -MMD -MP -MF"Drivers/CMSIS/system_stm32wlxx.d" -MT"$@" --specs=nano.specs -mfloat-abi=soft -mthumb -o "$@"

