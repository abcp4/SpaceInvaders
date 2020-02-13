#include <stdio.h>
#include <stdlib.h>
#include "list.h"



Node * createnode(int id,int x,int y);

Node * createnode(int id,int x,int y){
  Node * newNode = malloc(sizeof(Node));
  if (!newNode) {
    return NULL;
  }
  newNode->id = id;
  newNode->x = x;
  newNode->y = y;
  newNode->next = NULL;
  return newNode;
}

List * makelist(){
  List * list = malloc(sizeof(List));
  if (!list) {
    return NULL;
  }
  list->head = NULL;
  return list;
}

void display(List * list) {
  printf("current list elements: \n");
  Node * current = list->head;
  if(list->head == NULL)
    return;

  for(; current != NULL; current = current->next) {
    printf("%d\n", current->id);
  }
}

void add(int id, int x, int y, List * list){
  Node * current = NULL;
  if(list->head == NULL){
    list->head = createnode(id,x,y);
  }
  else {
    current = list->head;
    while (current->next!=NULL){
      current = current->next;
    }
    current->next = createnode(id,x,y);
  }
}

void search_delete(int id, List * list){
  Node * current = list->head;
  Node * previous = current;
  while(current != NULL){
    if(current->id == id){
      previous->next = current->next;
      if(current == list->head)
        list->head = current->next;
      free(current);
      return;
    }
    previous = current;
    current = current->next;
  }
}

void delete( List * list,Node * previous, Node * current){
  previous->next = current->next;
  if(current == list->head)
	list->head = current->next;
  free(current);
  return;
}

void reverse(List * list){
  Node * reversed = NULL;
  Node * current = list->head;
  Node * temp = NULL;
  while(current != NULL){
    temp = current;
    current = current->next;
    temp->next = reversed;
    reversed = temp;
  }
  list->head = reversed;
}

void destroy(List * list){
  Node * current = list->head;
  Node * next = current;
  while(current != NULL){
    next = current->next;
    free(current);
    current = next;
  }
  free(list);
  //list->head = NULL;
}
