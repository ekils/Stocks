read -p "輸入美股代號： " stock
export stock
python get_price.py 
python to_pe_ratio.py
python plot.py


