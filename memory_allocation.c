#include <stdio.h>
#define MAX 20

int main() {
    int block[MAX], original[MAX];
    int process[MAX], allocation[MAX];
    int b, p, choice;

    printf("Enter number of memory blocks: ");
    scanf("%d", &b);

    if (b <= 0 || b > MAX) {
        printf("Invalid number of blocks!\n");
        return 1;
    }

    printf("Enter block sizes:\n");
    for (int i = 0; i < b; i++) {
        scanf("%d", &block[i]);
        if (block[i] <= 0) {
            printf("Invalid block size!\n");
            return 1;
        }
        original[i] = block[i];
    }
    printf("Enter number of processes: ");
    scanf("%d", &p);

    if (p <= 0 || p > MAX) {
        printf("Invalid number of processes!\n");
        return 1;
    }
    printf("Enter process sizes:\n");
    for (int i = 0; i < p; i++) {
        scanf("%d", &process[i]);
        if (process[i] <= 0) {
            printf("Invalid process size!\n");
            return 1;
        }
        allocation[i] = -1;
    }
    printf("\n1. First Fit");
    printf("\n2. Best Fit");
    printf("\n3. Worst Fit");
    printf("\nChoose algorithm: ");
    scanf("%d", &choice);

    if (choice < 1 || choice > 3) {
        printf("Invalid choice!\n");
        return 1;
    }
    for (int i = 0; i < p; i++) {
        int selected = -1;
        for (int j = 0; j < b; j++) {
            if (block[j] >= process[i]) {
                if (selected == -1) {
                    selected = j;
                } else if (choice == 2 && block[j] < block[selected]) {
                    selected = j;
                } else if (choice == 3 && block[j] > block[selected]) {
                    selected = j;
                }
                if (choice == 1)
                    break;
            }
        }
        if (selected != -1) {
            allocation[i] = selected;
            block[selected] -= process[i];
        }
    }

    printf("\nProcess\tSize\tBlock\tStatus\n");

    for (int i = 0; i < p; i++) {
        if (allocation[i] != -1) {
            printf("P%d\t%d\tB%d\tAllocated\n", i + 1, process[i], allocation[i] + 1);
        }
        else {
            printf("P%d\t%d\t-\tNot Allocated\n",i + 1, process[i]);
        }
    }

    printf("\nRemaining block sizes:\n");
    for (int i = 0; i < b; i++) {
        printf("B%d: %d\n", i + 1, block[i]);
    }
    return 0;
}
