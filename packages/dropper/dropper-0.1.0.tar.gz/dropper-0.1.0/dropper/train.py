import numpy
import torch
import torchvision.datasets as datasets
from torch import nn, optim,mps, cuda
from torch.utils.data import DataLoader
from torchmetrics.functional import f1_score
from torchvision import transforms
from sklearn.metrics import roc_auc_score
from model import Dropper
def train_validate(batch_size = 16, lr=0.001, betas=(0.9, 0.999)):
    """
    Trains a Dropper model and saves the model parameters
    :param batch_size: size of training batches
    :param lr: the learning rates
    :param betas: B1 and B2 for the Adam Opmtimizer
    :return:
    """
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.247, 0.243, 0.261))
    ])
    train_set = datasets.CIFAR10(download=True, train=True, root='./data', transform=transform)
    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True)

    model = Dropper()
    criterion = nn.CrossEntropyLoss(reduction="mean")
    optimizer = optim.Adam(model.parameters(), lr=lr, betas=betas)
    model.train()
    dev = 'cpu'
    if mps.is_available():
        dev = 'mps'
    if cuda.is_available():
        dev = 'cuda'
    device = torch.device(dev)
    model = model.to(device)
    for epoch in range(15):
        running_loss = 0.0
        for i, data in enumerate(train_loader, 0):
            inputs, labels = data[0].to(device), data[1].to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        print(f'[Training Epoch {epoch + 1} Loss: {running_loss:.4f}]')
    validate(batch_size, device, model, transform)

def validate(batch_size, device, model, transform):
    """
    Shows performance outside training set.
    :param batch_size: the batch size to be used by the loader
    :param device: cuda, cpu, or mps depending on os
    :param model: the classifier itself
    :param transform: the transforms to be applied to the images from CIFAR10.
    :return:
    """
    test_criterion = nn.CrossEntropyLoss(reduction="mean")
    test_set = datasets.CIFAR10(root='./data', train=False,
                                download=True, transform=transform)
    testloader = DataLoader(test_set, shuffle=False)
    y_true = []
    y_pred_probs = []
    model.eval()
    with torch.no_grad():
        running_loss = 0.0
        for test_inputs, test_labels in testloader:
            test_inputs = test_inputs.to(device)
            test_labels = test_labels.to(device)
            outputs = model(test_inputs)
            loss = test_criterion(outputs, test_labels)
            running_loss += loss.item()
            probabilities = torch.softmax(outputs, dim=1).cpu().numpy()
            y_pred_probs.extend(probabilities)
            y_true.extend(test_labels.cpu().numpy())
    print(f'[Test Loss: {running_loss / (len(testloader) / batch_size):.4f}]')
    roc_auc = roc_auc_score(y_true, y_pred_probs, multi_class='ovr')
    y_true = torch.Tensor(numpy.array(y_true))
    y_pred_probs = torch.Tensor(numpy.array(y_pred_probs))
    f1 = f1_score(num_classes=10, target=y_true, preds=y_pred_probs, task="multiclass")
    print(f"F1 Score: {f1:.5f}")
    print(f"ROC AUC: {roc_auc:.5f}")
    torch.save(model.state_dict(), './dropper.pth')


if __name__ == "__main__":
    train_validate()