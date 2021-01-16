
#ifndef _UTILS_H
#define _UTILS_H

#define IRQ_QUEUE_MAX_SIZE 30

typedef struct
{
  uint8_t irq_status[4];	 /* The IRQ status */
  uint32_t timer;			/* The timer value in [us] */
}IrqItem;

typedef struct
{
  IrqItem xIrqQueue[IRQ_QUEUE_MAX_SIZE];		/* The queue values */
  uint8_t cIndexPush;                                   /* The push index */
  uint8_t cIndexPop;                                    /* The pop index */
  volatile uint8_t cIrqQueueSize;                       /* The size of the queue */
}IrqQueue;

uint32_t BufferToUint32(uint8_t* ucBuffer);


#endif /*_UTILS_H*/
