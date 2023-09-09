from django.core.management import BaseCommand


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
