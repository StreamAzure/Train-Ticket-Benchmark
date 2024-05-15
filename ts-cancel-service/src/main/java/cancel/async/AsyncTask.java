package cancel.async;

import java.util.Random;
import java.util.concurrent.Future;

import cancel.service.CancelServiceImpl;
import edu.fudan.common.entity.OrderStatus;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Async;
import org.springframework.scheduling.annotation.AsyncResult;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Component;
import edu.fudan.common.entity.Order;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import edu.fudan.common.util.Response;
import cancel.entity.*;

@Component
public class AsyncTask {

    @Autowired
    private RestTemplate restTemplate;

    private static final Logger LOGGER = LoggerFactory.getLogger(AsyncTask.class);

    @Async("myAsync")
    public Future<Response> updateOtherOrderStatusToCancel(Order order, HttpHeaders headers){
        AsyncTask.LOGGER.info("[Change Order Status] Changing....");
        try{
            Thread.sleep(1000);
        }catch (InterruptedException e){
            throw new RuntimeException(e);
        }
        order.setStatus(OrderStatus.CANCEL.getCode());
        HttpHeaders newHeaders = getAuthorizationHeadersFrom(headers);
        HttpEntity requestEntity = new HttpEntity(order, newHeaders);
        ResponseEntity<Response> re = restTemplate.exchange(
                "http://ts-order-other-service:12032/api/v1/orderOtherService/orderOther",
                HttpMethod.PUT,
                requestEntity,
                Response.class);
        return new AsyncResult<>(re.getBody());

    }

    public static HttpHeaders getAuthorizationHeadersFrom(HttpHeaders oldHeaders) {
        HttpHeaders newHeaders = new HttpHeaders();
        if (oldHeaders.containsKey(HttpHeaders.AUTHORIZATION)) {
            newHeaders.add(HttpHeaders.AUTHORIZATION, oldHeaders.getFirst(HttpHeaders.AUTHORIZATION));
        }
        return newHeaders;
    }

    @Async("mySimpleAsync")
    public Future<Boolean> drawBackMoneyForOrderCancel(HttpHeaders headers, String money, String userId,String orderId){

        /*********************** Fault Reproduction - Error Process Seq *************************/
        double op = new Random().nextDouble();
       if(op < 0.5){
           System.out.println("[Cancel Order Service] Delay Process，Wrong Cancel Process");
           try{
                Thread.sleep(2000);
           }catch (InterruptedException e){
                throw new RuntimeException(e);
           }
       } else {
           System.out.println("[Cancel Order Service] Normal Process，Normal Cancel Process");
       }

        // AsyncTask.LOGGER.info("[Cancel Order Service] Delay Process，Wrong Cancel Process");
        // try {
        //     Thread.sleep(5000);
        // } catch (InterruptedException e) {
        //     throw new RuntimeException(e);
        // }

        //1.Search Order Info
        AsyncTask.LOGGER.info("[Cancel Order Service][Get Order] Getting....");
        HttpHeaders newHeaders = getAuthorizationHeadersFrom(headers);
        HttpEntity requestEntity = new HttpEntity(newHeaders);
        ResponseEntity<Response<Order>> re = restTemplate.exchange(
                "http://ts-order-other-service:12032/api/v1/orderOtherService/orderOther/" + orderId,
                HttpMethod.GET,
                requestEntity,
                new ParameterizedTypeReference<Response<Order>>() {
                });
        Order order = re.getBody().getData();
        //2.Change order status to cancelling
        order.setStatus(OrderStatus.CANCELING.getCode());
        HttpEntity cancellingRequestEntity = new HttpEntity(order, newHeaders);
        ResponseEntity<Response> re2 = restTemplate.exchange(
                "http://ts-order-other-service:12032/api/v1/orderOtherService/orderOther",
                HttpMethod.PUT,
                cancellingRequestEntity,
                Response.class);
        Response response = re2.getBody();
        if(response.getStatus() == 0){
            AsyncTask.LOGGER.info("[Cancel Order Service]Unexpected error");
        }
        //3.do drawback money
        AsyncTask.LOGGER.info("[Cancel Order Service][Draw Back Money] Draw back money...");

        ResponseEntity<Response> re3 = restTemplate.exchange(
                "http://ts-inside-payment-service:18673/api/v1/inside_pay_service/inside_payment/drawback/" + userId + "/" + money,
                HttpMethod.GET,
                requestEntity,
                Response.class);
        Response result = re3.getBody();

        if(result.getStatus() == 1){
            return new AsyncResult<>(true);
        }else{
            return new AsyncResult<>(false);
        }
        /*****************************************************************************/
    }
}