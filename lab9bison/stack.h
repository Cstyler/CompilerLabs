
typedef struct {
    unsigned int ident_num;
} NODE_DATA;

typedef struct node {
    NODE_DATA data;
    struct node* prev;
} NODE;

void st_init(NODE** top) {
    *top = NULL;
}

NODE* st_push(NODE* top, NODE_DATA data) {
    NODE* tmp = (NODE*) malloc(sizeof (NODE));
    if (tmp == NULL) {
        printf("Out of memory!");
				return NULL;
    }
    tmp->data = data;
    tmp->prev = top;
    top = tmp;
    return top;
}

NODE* st_pop(NODE *top, NODE_DATA *element) {
    NODE* tmp = top;
    *element = top->data;
    top = top->prev;
    free(tmp);
    return top;
}

NODE_DATA* st_peek(NODE *top) {
    return &top->data;
}

int st_is_empty(NODE* top) {
    return (top == NULL) ? 1 : 0;
}

void st_free(NODE* st) {
  NODE_DATA element;
  while (!st_is_empty(st)) {
        st = st_pop(st, &element);
  }
}
