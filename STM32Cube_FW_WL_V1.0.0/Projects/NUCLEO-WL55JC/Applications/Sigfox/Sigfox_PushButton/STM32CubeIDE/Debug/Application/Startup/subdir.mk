################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
S_SRCS += \
../Application/Startup/startup_stm32wl55jcix.s 

OBJS += \
./Application/Startup/startup_stm32wl55jcix.o 

S_DEPS += \
./Application/Startup/startup_stm32wl55jcix.d 


# Each subdirectory must supply rules for building sources it contributes
Application/Startup/startup_stm32wl55jcix.o: ../Application/Startup/startup_stm32wl55jcix.s
	arm-none-eabi-gcc -mcpu=cortex-m4 -g3 -c -x assembler-with-cpp -MMD -MP -MF"Application/Startup/startup_stm32wl55jcix.d" -MT"$@" --specs=nano.specs -mfloat-abi=soft -mthumb -o "$@" "$<"

