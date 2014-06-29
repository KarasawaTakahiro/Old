#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void printField(int num, int stage){
	int i, j;
	int printed = 0;
	int blank;

	blank = stage - 1;

	for(i=0; i<stage; i++){
		for(j=0; j<blank; j++){
			printf(" ");
		}
		blank--;
		for(j=0; j<=i; j++){
			if(num <= printed){
				break;
			}
			printf("| ");
			printed++;
		}
		printf("\n");
	}
	return ;
}

int field(int stage){
	// stage: 段数
	int num=0;
	int i;
	for(i=1; i<=stage; i++){
		num += i;
	}
	return num;
}

void player(int* num){
	int fig;
	int flag=0;
	printf("何本とりますか？\n>>> ");
	while(!flag){
		scanf("%d", &fig);
		if(*num < fig){
			printf("数が多すぎます。もう一度入力してください。\n>>> ");
		}
		if(0 < fig && fig <= 3){
			flag = 1;
		}else{
			printf("1〜3の数字を入力してください\n>>> ");
		}
	}
	*num -= fig;
	return ;
}

void cp(int* num){
	int fig;
	fig = 3 - *num % 4;
	if(fig == 0){fig = 2;}
	printf("%d本取ります。\n", fig);
	*num -= fig;
	return ;
}

int defFirstMove(void){
	/* cp:0
	 * player:1
	 */
	int first;
	int cp;
	int player;
	cp = rand() % 2 + 1;
	printf("先行を決めます。");
	printf("偶数だと思ったら「0」、奇数だと思ったら「1」を入力\n>> ");
	while(1){
		scanf("%d", &player);
		if(player == 1 || player == 0){
			break;
		}else{
			printf("値が不正です。\n偶数だと思ったら「0」、奇数だと思ったら「1」を入力\n>> ");
		}
	}
	printf("CP: %d, Player: ", cp);
	if(player){
		printf("奇数\n");
	}else{
		printf("偶数\n");
	}
	if(player == cp){
		first = 1;
		printf("Playerの先手です。\n");
	}else{
		first = 0;
		printf("CPの先手です。\n");
	}
	return first;
}

int main(void){
	int num;  // 棒の数
	int stage=-1;  // 段数
	int turn=1;  // ターン数
	int first;  // 先手
	int br;
	srand(time(NULL));

	printf("段数を入力してください。3段以上にしてね。\n>> ");
	while(stage < 3){
		scanf("%d", &stage);
		if(stage < 3){
			printf("3以上の数を入力してください。\n>> ");
		}
	}
	num = field(stage);
	first = defFirstMove();  // 順番決め
	printField(num, stage);

	printf("段数: %d\n数: %d\n", stage, num);
	printf("ゲームスタート!!\n");
	while(num > 1){
		printf("===========================================\n");
		printf("%dターン目\n", turn);
		printField(num, stage);
		if(first % 2 == 0){
			printf("CPの番です。\n");
			cp(&num);
			br = getchar();
		}else{
			printf("Playerの番です。\n");
			player(&num);
		}
	printf("\n");
	first++;
	turn++;
	}

	printf("===========================================\n");
	printField(num, stage);
	if(first % 2 == 0){
		printf("あなたの勝ちです!!");
	}else{
		printf("あなたの負けです!!");
	}

	return 0;
}

