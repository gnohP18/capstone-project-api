# Capstone project by `NGUYEN HOANG PHONG` aka `shubanoname`

## DA NANG UNIVERSITY OF SCIENCE AND TECHNOLOGY

### Service

[Elastic](https://www.elastic.co/)

[logstash](https://www.elastic.co/logstash)

[kibana](https://www.elastic.co/kibana)

[Python-3.9.2](https://www.python.org/)

### How to use

#### With `docker` (required install docker)

```code
docker compose up -d --build
```

### Network port

|  No | Container  | Default port | Custom port  | private |
|---|---|---|---|---|
| 1 | elasticsearch | 9200, 9300 | 9200, 9300 | No |
| 2 | kibana | 5601 | 5601 | No  |
| 3 | logstash | 5044, 9600 | 5044, 9600 | No |
| 4 | python-api | 8080 | 8123 | No |

### Reference template

[Github](https://github.com/deviantony/docker-elk)
