#include <stdio.h>
#define MAX 20

int main() {
    int n, m;
    int processIds[MAX];
    int allocation[MAX][MAX];
    int request[MAX][MAX];
    int available[MAX], work[MAX];
    int finish[MAX] = {0};
    int deadlock = 0, progress;

    printf("Enter number of processes and resources: ");
    scanf("%d %d", &n, &m);

    if (n <= 0 || n > MAX || m <= 0 || m > MAX) {
        printf("Invalid input!\n");
        return 1;
    }
    printf("Enter process IDs:\n");
    for (int i = 0; i < n; i++) {
        scanf("%d", &processIds[i]);
    }
    printf("Enter Allocation Matrix:\n");
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            scanf("%d", &allocation[i][j]);
            if (allocation[i][j] < 0) return 1;
        }
    }

    printf("Enter Request Matrix:\n");
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            scanf("%d", &request[i][j]);
            if (request[i][j] < 0) return 1;
        }
    }

    printf("Enter Available Resources:\n");
    for (int j = 0; j < m; j++) {
        scanf("%d", &available[j]);
        if (available[j] < 0) return 1;
        work[j] = available[j];
    }

    for (int i = 0; i < n; i++) {
        int hasResource = 0;

        for (int j = 0; j < m; j++) {
            if (allocation[i][j] > 0)
                hasResource = 1;
        }

        if (!hasResource)
            finish[i] = 1;
    }

    do {
        progress = 0;

        for (int i = 0; i < n; i++) {
            if (finish[i])
                continue;

            int canFinish = 1;

            for (int j = 0; j < m; j++) {
                if (request[i][j] > work[j])
                    canFinish = 0;
            }

            if (canFinish) {
                for (int j = 0; j < m; j++)
                    work[j] += allocation[i][j];

                finish[i] = 1;
                progress = 1;
            }
        }
    } while (progress);

    for (int i = 0; i < n; i++) {
        if (!finish[i]) {
            printf("Potential deadlock detected!\n");
            printf("Process %d cannot finish.\n", processIds[i]);
            deadlock = 1;
        }
    }

    if (!deadlock)
        printf("No deadlock detected!\n");

    return 0;
}