/etc/init.d/elasticsearch start;
/etc/init.d/rabbitmq-server start;
zsh -c "python3 app.py &!"
