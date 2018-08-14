#pragma once

#include <string>
#include <vector>

#include <onnx/onnx.pb.h>

namespace oniku {

class Node;
class Tensor;
class Type;

class Value {
public:
    enum class Kind {
        kInput,
        kOutput,
        kTemp,
    };

    Value(const onnx::ValueInfoProto& xvalue, Kind kind);
    explicit Value(const std::string& name, Kind kind = Kind::kTemp);
    Value(const std::string& name, const Type& type, Kind kind = Kind::kTemp);
    ~Value();

    Value(const Value&) = delete;
    Value& operator=(const Value&) = delete;

    void ToONNX(onnx::ValueInfoProto* xvalue) const;

    Kind kind() const {
        return kind_;
    }
    const std::string& name() const {
        return name_;
    }
    const Type* type() const {
        return type_.get();
    }
    const std::string& doc_string() const {
        return doc_string_;
    }

    const Tensor* initializer() const {
        return initializer_.get();
    }
    void ResetInitializer(std::unique_ptr<Tensor>&& tensor);

    const std::vector<Node*>& users() const {
        return users_;
    }
    void AddUser(Node* user);

    const Node* producer() const {
        return producer_;
    }
    void SetProducer(Node* producer);

private:
    Kind kind_;
    std::string name_;
    std::unique_ptr<Type> type_;
    std::string doc_string_;
    std::unique_ptr<Tensor> initializer_;

    std::vector<Node*> users_;
    Node* producer_ = nullptr;
};

}  // namespace oniku
