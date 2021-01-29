################################################################################
# Automatically-generated file. Do not edit!
################################################################################

-include ../makefile.init

RM := rm -rf

# All of the sources participating in the build are defined here
-include sources.mk
-include Utilities/subdir.mk
-include Middlewares/SubGHz_Phy/subdir.mk
-include Middlewares/Sigfox/subdir.mk
-include Drivers/STM32WLxx_HAL_Driver/subdir.mk
-include Drivers/CMSIS/subdir.mk
-include Application/Target/subdir.mk
-include Application/Startup/subdir.mk
-include Application/Core/subdir.mk
-include Application/App/subdir.mk
-include subdir.mk
-include objects.mk

ifneq ($(MAKECMDGOALS),clean)
ifneq ($(strip $(S_DEPS)),)
-include $(S_DEPS)
endif
ifneq ($(strip $(S_UPPER_DEPS)),)
-include $(S_UPPER_DEPS)
endif
ifneq ($(strip $(C_DEPS)),)
-include $(C_DEPS)
endif
endif

-include ../makefile.defs

BUILD_ARTIFACT_NAME := Sigfox_PushButton
BUILD_ARTIFACT_EXTENSION := elf
BUILD_ARTIFACT_PREFIX := 
BUILD_ARTIFACT := $(BUILD_ARTIFACT_PREFIX)$(BUILD_ARTIFACT_NAME).$(BUILD_ARTIFACT_EXTENSION)

# Add inputs and outputs from these tool invocations to the build variables 
EXECUTABLES += \
Sigfox_PushButton.elf \

SIZE_OUTPUT += \
default.size.stdout \

OBJDUMP_LIST += \
Sigfox_PushButton.list \

OBJCOPY_BIN += \
Sigfox_PushButton.bin \


# All Target
all: main-build

# Main-build Target
main-build: Sigfox_PushButton.elf secondary-outputs

# Tool invocations
Sigfox_PushButton.elf: $(OBJS) $(USER_OBJS) C:\Users\name\Desktop\STM32Cube_FW_WL_V1.0.0\Current\STM32Cube_FW_WL_V1.0.0\Projects\NUCLEO-WL55JC\Applications\Sigfox\Sigfox_PushButton\STM32CubeIDE\STM32WL55JCIX_FLASH.ld
	arm-none-eabi-gcc -o "Sigfox_PushButton.elf" @"objects.list" $(USER_OBJS) $(LIBS) -mcpu=cortex-m4 -T"C:\Users\name\Desktop\STM32Cube_FW_WL_V1.0.0\Current\STM32Cube_FW_WL_V1.0.0\Projects\NUCLEO-WL55JC\Applications\Sigfox\Sigfox_PushButton\STM32CubeIDE\STM32WL55JCIX_FLASH.ld" --specs=nosys.specs -Wl,-Map="Sigfox_PushButton.map" -Wl,--gc-sections -static -L../../../../../../../Middlewares/Third_Party/Sigfox/SigfoxLibTest -L../../../../../../../Middlewares/Third_Party/Sigfox/Monarch -L../../../../../../../Middlewares/Third_Party/Sigfox/SigfoxLib -L../../../../../../../Middlewares/Third_Party/Sigfox/Crypto --specs=nano.specs -mfloat-abi=soft -mthumb -Wl,--start-group -lc -lm -Wl,--end-group
	@echo 'Finished building target: $@'
	@echo ' '

default.size.stdout: $(EXECUTABLES)
	arm-none-eabi-size  $(EXECUTABLES)
	@echo 'Finished building: $@'
	@echo ' '

Sigfox_PushButton.list: $(EXECUTABLES)
	arm-none-eabi-objdump -h -S $(EXECUTABLES) > "Sigfox_PushButton.list"
	@echo 'Finished building: $@'
	@echo ' '

Sigfox_PushButton.bin: $(EXECUTABLES)
	arm-none-eabi-objcopy  -O binary $(EXECUTABLES) "Sigfox_PushButton.bin"
	@echo 'Finished building: $@'
	@echo ' '

# Other Targets
clean:
	-$(RM) *
	-@echo ' '

secondary-outputs: $(SIZE_OUTPUT) $(OBJDUMP_LIST) $(OBJCOPY_BIN)

fail-specified-linker-script-missing:
	@echo 'Error: Cannot find the specified linker script. Check the linker settings in the build configuration.'
	@exit 2

warn-no-linker-script-specified:
	@echo 'Warning: No linker script specified. Check the linker settings in the build configuration.'

.PHONY: all clean dependents fail-specified-linker-script-missing warn-no-linker-script-specified
.SECONDARY:

-include ../makefile.targets
