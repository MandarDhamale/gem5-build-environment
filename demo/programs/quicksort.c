#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// Swap utility
void swap(int *a, int *b)
{
    int t = *a;
    *a = *b;
    *b = t;
}

// Partition function for Quick Sort
int partition(int arr[], int low, int high)
{
    int pivot = arr[high];
    int i = (low - 1);
    for (int j = low; j <= high - 1; j++)
    {
        if (arr[j] < pivot)
        {
            i++;
            swap(&arr[i], &arr[j]);
        }
    }
    swap(&arr[i + 1], &arr[high]);
    return (i + 1);
}

// Main Quick Sort algorithm
void quickSort(int arr[], int low, int high)
{
    if (low < high)
    {
        int pi = partition(arr, low, high);
        quickSort(arr, low, pi - 1);
        quickSort(arr, pi + 1, high);
    }
}

int main()
{
    int n = 500; // Array size for the benchmark
    int *arr = (int *)malloc(n * sizeof(int));

    // Seed and populate array with random numbers
    srand(42);
    for (int i = 0; i < n; i++)
    {
        arr[i] = rand() % 100000;
    }

    printf("Starting Quick Sort on %d elements...\n", n);

    // Track execution time
    clock_t start = clock();
    quickSort(arr, 0, n - 1);
    clock_t end = clock();

    double time_taken = ((double)(end - start)) / CLOCKS_PER_SEC;
    printf("Quick Sort completed in %f seconds.\n", time_taken);

    free(arr);
    return 0;
}