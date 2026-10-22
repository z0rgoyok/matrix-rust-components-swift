# Выпуск Tich Connect SDK

Swift package поставляет библиотеку из нашего `z0rgoyok/matrix-rust-sdk`.
Источник предварительно проходит PR, проверки и merge в `tich/main`.

1. В чистом checkout SDK выполнить `scripts/tich-build-apple.sh`.
2. Здесь выполнить `python3 Tools/prepare-tich-release.py --sdk <checkout>
   --version 26.10.21`, выбрав новый номер версии.
3. Проверить `tich-source.json`, Swift bindings и `Package.swift`, создать PR
   в этот форк, дождаться проверок, merge.
4. Создать GitHub release на merged SHA с тем же тегом и приложить архив
   `.automate/<version>/MatrixSDKFFI.xcframework.zip` и `tich-source.json`.
5. В отдельном PR приложения закрепить URL нашего package и exactVersion.

Не заменять архив существующего release: для исправления выпускается новая
версия. Квитанция связывает исходники, компилятор, файлы framework и checksum
поставляемого архива. После проверки скачать архив выпуска и сверить checksum.

Для интеграции с Element Call используйте числовую stable-версию: его диапазон зависимостей исключает prerelease.
