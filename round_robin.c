#include <stdio.h>
#define MAX 20

int main() {
    int n, quantum;
    int bt[MAX], remaining[MAX];
    int waiting[MAX] = {0};
    int turnaround[MAX] = {0};
    int time = 0, completed = 0;

    printf("Enter number of processes: ");
    scanf("%d", &n);

    if (n <= 0 || n > MAX) {
        printf("Invalid number of processes!\n");
        return 1;
    }

    printf("Enter burst times:\n");
    for (int i = 0; i < n; i++) {
        scanf("%d", &bt[i]);

        if (bt[i] <= 0) {
            printf("Invalid burst time!\n");
            return 1;
        }

        remaining[i] = bt[i];
    }

    printf("Enter time quantum: ");
    scanf("%d", &quantum);

    if (quantum <= 0) {
        printf("Invalid time quantum!\n");
        return 1;
    }

    while (completed < n) {
        for (int i = 0; i < n; i++) {
            if (remaining[i] > 0) {
                if (remaining[i] > quantum) {
                    time += quantum;
                    remaining[i] -= quantum;
                } else {
                    time += remaining[i];
                    remaining[i] = 0;
                    turnaround[i] = time;
                    waiting[i] = turnaround[i] - bt[i];
                    completed++;
                }
            }
        }
    }

    printf("\nProcess\tBurst\tWaiting\tTurnaround\n");

    float totalWaiting = 0, totalTurnaround = 0;

    for (int i = 0; i < n; i++) {
        printf("P%d\t%d\t%d\t%d\n", i + 1, bt[i], waiting[i], turnaround[i]);
        totalWaiting += waiting[i];
        totalTurnaround += turnaround[i];
    }
    printf("\nAverage Waiting Time: %.2f\n", totalWaiting / n);
    printf("Average Turnaround Time: %.2f\n", totalTurnaround / n);
    return 0;
}
