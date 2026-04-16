/*
 * Quicksort Benchmark - Instrumented with gem5 m5ops ROI markers
 * Uses inline assembly to emit the gem5 pseudo-instructions directly
 * (no libm5 linkage needed for SE mode x86)
 *
 * m5_dump_reset_stats: opcode 0x42
 * x86 encoding:  0x0F 0x04 <16-bit opcode>
 */

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdint.h>

/* ---- Inline gem5 m5ops for x86 -----------------------------------------
 * The gem5 pseudo-instruction for x86 is:
 *   .byte 0x0F, 0x04   (escape prefix)
 *   .word  <func>       (16-bit function code)
 *
 * Arguments are passed in rdi, rsi (System V AMD64 ABI).
 * We use inline asm so the compiler handles register allocation.
 */
static inline void m5_dump_reset_stats(uint64_t ns_delay, uint64_t ns_period)
{
    __asm__ volatile (
        ".byte 0x0F, 0x04\n\t"
        ".word 0x0042\n\t"   /* M5OP_DUMP_RESET_STATS = 0x42 */
        :
        : "D" (ns_delay), "S" (ns_period)
        : "memory"
    );
}

/* ---- Quicksort implementation ------------------------------------------ */

void swap(int *a, int *b)
{
    int t = *a;
    *a = *b;
    *b = t;
}

int partition(int arr[], int low, int high)
{
    int pivot = arr[high];
    int i = (low - 1);
    for (int j = low; j <= high - 1; j++) {
        if (arr[j] < pivot) {
            i++;
            swap(&arr[i], &arr[j]);
        }
    }
    swap(&arr[i + 1], &arr[high]);
    return (i + 1);
}

void quickSort(int arr[], int low, int high)
{
    if (low < high) {
        int pi = partition(arr, low, high);
        quickSort(arr, low, pi - 1);
        quickSort(arr, pi + 1, high);
    }
}

int main(int argc, char *argv[])
{
    /* Array size can be passed as argv[1]; default to ARRAY_SIZE macro or 10000 */
#ifdef ARRAY_SIZE
    int n = ARRAY_SIZE;
#else
    int n = (argc > 1) ? atoi(argv[1]) : 10000;
#endif

    int *arr = (int *)malloc(n * sizeof(int));
    if (!arr) {
        fprintf(stderr, "malloc failed for n=%d\n", n);
        return 1;
    }

    /* Seed and populate array with random numbers */
    srand(42);
    for (int i = 0; i < n; i++) {
        arr[i] = rand() % 1000000;
    }

    printf("Starting Quick Sort on %d elements...\n", n);

    /* ---- ROI BEGIN: dump & reset stats just before sorting ------------- */
    m5_dump_reset_stats(0, 0);

    quickSort(arr, 0, n - 1);

    /* ---- ROI END: dump & reset stats just after sorting --------------- */
    m5_dump_reset_stats(0, 0);

    printf("Quick Sort completed.\n");

    free(arr);
    return 0;
}
