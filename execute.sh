/etc/init.d/elasticsearch start;
/etc/init.d/rabbitmq-server start;
zsh -c "celery -A api.gyresources.logic.tf_serving_client worker --loglevel=info &!" 
zsh -c "python3 app.py"
