import os
import pickle

from django.core.management import BaseCommand
from tqdm import tqdm

from apps.log_service.algorithm.drain3.template_miner import TemplateMiner
from apps.log_service.algorithm.drain3.template_miner_config import TemplateMinerConfig

# 常量定义
CONFIG_FILE_PATH = '../algorithm/drain3/drain3.ini'
PROFILING_ENABLED = False


class Command(BaseCommand):
    help = '训练LogReduce模型'

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

        data_dir = options["data_dir"]
        model_dir = options["model_dir"]
        algorithm = options["algorithm"]

        if algorithm == "drain3":
            config = TemplateMinerConfig()
            config_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_FILE_PATH)
            config.load(config_file_path)
            config.profiling_enabled = PROFILING_ENABLED
            template_miner = TemplateMiner(config=config)

            # 遍历data_dir目录下的所有日志文件
            files = os.listdir(data_dir)
            # 循环读取files
            for file in files:
                file_path = os.path.join(data_dir, file)
                with open(file_path, 'r') as file:
                    logs = file.readlines()
                    for log in tqdm(logs):
                        log = log.rstrip()
                        log = log.partition(": ")[2]
                        template_miner.add_log_message(log)

            # 保存训练好的template_miner模型
            with open(model_dir, "wb") as file:
                pickle.dump(template_miner, file)

        elif algorithm == "spell":
            pass
