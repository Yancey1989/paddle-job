import gzip
import math
import pickle
import paddle.v2 as paddle
import paddle.job as job

import os
embsize = 32
hiddensize = 256
N = 5

TRAIN_DATA_PATH="/data/yanxu/word2vec/train.txt"
TEST_DATA_PATH="/data/yanxu/word2vec/test.txt"
WORD_DICT_PATH="/data/yanxu/word2vec/word_dict.pickle"
TRAINERS=int(os.getenv("TRAINERS", "1"))

def wordemb(inlayer):
    wordemb = paddle.layer.embedding(
        input=inlayer,
        size=embsize,
        param_attr=paddle.attr.Param(
            name="_proj",
            initial_std=0.001,
            learning_rate=1,
            l2_rate=0,
            sparse_update=True))
    return wordemb


def fetch_trainer_id():
    return int(os.getenv("PADDLE_INIT_TRAINER_ID", 0))

def fetch_pserver_ips():
    return os.getenv("PADDLE_INIT_PSERVERS", "")

def dist_reader(filename, trainers, trainer_id):
    def dist_reader_creator():
        with open (filename) as f:
            cnt = 0
            for line in f:
                cnt += 1
                if cnt % trainers == trainer_id:
                    csv_data = [int(cell) for cell in line.split(",")]
                    yield tuple(csv_data)
    return dist_reader_creator

def dist_trainer():
    def trainer_creator():
        paddle.init(use_gpu=False,
                    trainer_count=1,
                    port=7164,
                    num_gradient_servers=1,
                    ports_num=1,
                    ports_num_for_sparse=1,
                    trainer_id=fetch_trainer_id(),
                    pservers=fetch_pserver_ips())
        with open(WORD_DICT_PATH) as f:
            word_dict = pickle.load(f)
        dict_size = len(word_dict)
        firstword = paddle.layer.data(
            name="firstw", type=paddle.data_type.integer_value(dict_size))
        secondword = paddle.layer.data(
            name="secondw", type=paddle.data_type.integer_value(dict_size))
        thirdword = paddle.layer.data(
            name="thirdw", type=paddle.data_type.integer_value(dict_size))
        fourthword = paddle.layer.data(
            name="fourthw", type=paddle.data_type.integer_value(dict_size))
        nextword = paddle.layer.data(
            name="fifthw", type=paddle.data_type.integer_value(dict_size))

        Efirst = wordemb(firstword)
        Esecond = wordemb(secondword)
        Ethird = wordemb(thirdword)
        Efourth = wordemb(fourthword)

        contextemb = paddle.layer.concat(input=[Efirst, Esecond, Ethird, Efourth])
        hidden1 = paddle.layer.fc(input=contextemb,
                                  size=hiddensize,
                                  act=paddle.activation.Sigmoid(),
                                  layer_attr=paddle.attr.Extra(drop_rate=0.5),
                                  bias_attr=paddle.attr.Param(learning_rate=2),
                                  param_attr=paddle.attr.Param(
                                      initial_std=1. / math.sqrt(embsize * 8),
                                      learning_rate=1))
        predictword = paddle.layer.fc(input=hidden1,
                                      size=dict_size,
                                      bias_attr=paddle.attr.Param(learning_rate=2),
                                      act=paddle.activation.Softmax())

        cost = paddle.layer.classification_cost(input=predictword, label=nextword)

        parameters = paddle.parameters.create(cost)
        adagrad = paddle.optimizer.AdaGrad(
            learning_rate=3e-3,
            regularization=paddle.optimizer.L2Regularization(8e-4))
        trainer = paddle.trainer.SGD(cost,
                                     parameters,
                                     adagrad,
                                     is_local=False)
        def event_handler(event):
            if isinstance(event, paddle.event.EndIteration):
                 if event.batch_id % 100 == 0:
                     with gzip.open("batch-" + str(event.batch_id) + ".tar.gz",
                       'w') as f:
                         trainer.save_parameter_to_tar(f)
                         result = trainer.test(
                            paddle.batch(
                                dist_reader(TEST_DATA_PATH, TRAINERS, fetch_trainer_id()),32))
                         print "Pass %d, Batch %d, Cost %f, %s, Testing metrics %s" % (
                            event.pass_id, event.batch_id, event.cost, event.metrics,
                            result.metrics)
        trainer.train(
            reader=paddle.batch(
                reader=dist_reader(TRAIN_DATA_PATH, TRAINERS, fetch_trainer_id()),
                batch_size=32),
            num_passes=1,
            event_handler=event_handler)
    return trainer_creator
def main():
    paddle_job=job.PaddleJob(
        runtime_image="yancey1989/paddle-job",
        job_name="paddle-job",
        cpu_nums=3,
        trainer_package="/example/word2vec",
        entry_point="python train.py",
        cephfs_volume=job.CephFSVolume(
            monitors_addr="172.19.32.166:6789"
        ))
    job.dist_train(
        trainer=dist_trainer(),
        paddle_job=paddle_job)
if __name__ == '__main__':
    main()
