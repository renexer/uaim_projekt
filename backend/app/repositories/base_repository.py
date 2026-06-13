from app.extensions import db


# Bazowe repozytorium z prostymi operacjami zapisu, odczytu i usuwania encji.
class BaseRepository:
    model = None

    # Konstruktor inicjalizuje zależności potrzebne do działania klasy.
    def __init__(self, session=None):
        self.session = session or db.session

    # Dodaje encję do bieżącej sesji bazy danych i zwraca ją do dalszego użycia.
    def add(self, entity):
        self.session.add(entity)
        return entity

    # Pobiera encję po identyfikatorze z użyciem modelu przypisanego do repozytorium.
    def get(self, entity_id):
        return self.model.query.get(entity_id)

    # Oznacza encję do usunięcia w bieżącej sesji bazy danych.
    def delete(self, entity):
        self.session.delete(entity)

    # Zatwierdza wszystkie zmiany wykonane w bieżącej transakcji.
    def commit(self):
        self.session.commit()

    # Wysyła zmiany do bazy bez końcowego zatwierdzania transakcji.
    def flush(self):
        self.session.flush()
