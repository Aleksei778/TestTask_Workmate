# Логика добавления нового отчёта

Для добавления нового отчета необходимо опираться на следующие правила:
1. Необходимо создать новый класс отчета
- унаследовать новый класс от абстрактного класса ReportFabric
- реализовать все абстрактные методы, описанные в абстрактном классе
2. Необходимо добавить имя отчета в словарь ```available_reports = {"handlers": HandlersReport} ```
3. В функции process_log_file будет создаваться нужный экземпляр класса отчета в зависимости от имени, которое передается в параметрах.
4. Тесты написаны для отдельного класса отчета HandlersReport для того, чтобы соблюдался принцип изоляции в модульном тестировании.