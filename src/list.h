#ifndef LINKEDLIST_HEADER
#define LINKEDLIST_HEADER

typedef struct node Node;

typedef struct list List;

struct node {
  int id;
  int x;
  int y;
  struct node * next;
};

struct list {
  Node * head;
};

List * makelist();
void add(int id,int x, int y, List * list);
void search_delete(int id, List * list);
void delete( List * list, Node * previous, Node * current);

void display(List * list);
void reverse(List * list);
void destroy(List * list);

#endif
