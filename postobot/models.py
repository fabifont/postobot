from datetime import datetime
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime

Base = declarative_base()


def timestamp(context):
  date = context.get_current_parameters()['data_lezione']
  time = context.get_current_parameters()['ora_inizio_lezione']
  return datetime.strptime(f"{date} {time}", "%d/%m/%Y %H:%M")


class Lecture(Base):
  __tablename__ = 'lectures'
  entry_id = Column(Integer, primary_key=True)
  sede = Column(String)
  aula = Column(String)
  data_lezione = Column("data_lezione", String)
  ora_inizio = Column(String)
  ora_fine = Column(String)
  qr = Column(String)
  nome = Column(String)
  ora_inizio_lezione = Column("ora_inizio_lezione", String)
  ora_fine_lezione = Column(String)
  lecture_timestamp = Column(DateTime(timezone=False), default=timestamp)

  def __repr__(self):
    return f"{self.__class__}: {self.__dict__}"

  def __str__(self):
    return f"{self.entry_id} {self.data_lezione} {self.ora_inizio_lezione}-{self.ora_fine_lezione}\n{self.nome}\n{self.sede} {self.aula}"
