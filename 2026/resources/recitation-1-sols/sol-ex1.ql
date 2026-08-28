import javascript

from Function f
where
  exists(f.getABodyStmt()) and
  not exists(IfStmt r | r.getContainer() = f)
select f