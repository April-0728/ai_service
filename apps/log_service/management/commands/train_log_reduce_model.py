import os
import pickle

from django.core.management import BaseCommand

from apps.log_service.algorithm.drain3.template_miner import TemplateMiner
from apps.log_service.algorithm.drain3.template_miner_config import TemplateMinerConfig


class Command(BaseCommand):
    help = '训练LogRecude模型'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--data_dir', type=str, help='日志数据集目录')
        parser.add_argument('-m', '--model_dir', type=str, help='模型保存目录')
        parser.add_argument('-a', '--algorithm', type=str, help='算法名称:spell,drain3')
        parser.add_argument('-c', '--algorithm_config', type=str, help='算法参数配置文件路径')

    def handle(self, *args, **options):
        # 打印参数到控制台日志中
        self.stdout.write('data_dir: %s' % options['data_dir'])
        self.stdout.write('model_dir: %s' % options['model_dir'])
        self.stdout.write('algorithm: %s' % options['algorithm'])
        self.stdout.write('algorithm_config: %s' % options['algorithm_config'])

        # TODO: 训练LogReduce模型
        data_dir = options["data_dir"]
        model_dir = options["model_dir"]
        algorithm = options["algorithm"]

        if algorithm=="drain3":
            config = TemplateMinerConfig()
            current_directory = os.path.dirname(os.path.abspath(__file__))
            config_file_path = os.path.join(current_directory, '../algorithm/drain3/drain3.ini')
            config.load(config_file_path)
            config.profiling_enabled = False
            template_miner = TemplateMiner(config=config)

            with open(data_dir) as f:
                logs = f.readlines()

            # 训练模型
            for log in logs:
                log = log.rstrip()
                log = log.partition(": ")[2]
                result = template_miner.add_log_message(log)

            #保存训练好的template_miner模型
            with open(model_dir, "wb") as f:
                pickle.dump(template_miner, f)


        elif algorithm=="spell":
            pass