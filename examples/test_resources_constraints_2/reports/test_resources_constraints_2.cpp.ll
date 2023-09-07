; ModuleID = 'src/test_resources_constraints_2.cpp'
source_filename = "src/test_resources_constraints_2.cpp"
target datalayout = "e-m:e-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

; Function Attrs: noinline nounwind uwtable
define i32 @_Z28test_resources_constraints_2iiii(i32 %a, i32 %b, i32 %c, i32 %n) #0 {
entry:
  %a.addr = alloca i32, align 4
  %b.addr = alloca i32, align 4
  %c.addr = alloca i32, align 4
  %n.addr = alloca i32, align 4
  store i32 %a, i32* %a.addr, align 4
  store i32 %b, i32* %b.addr, align 4
  store i32 %c, i32* %c.addr, align 4
  store i32 %n, i32* %n.addr, align 4
  %0 = load i32, i32* %a.addr, align 4
  %div = sdiv i32 %0, 2
  %1 = load i32, i32* %b.addr, align 4
  %mul = mul nsw i32 %1, 3
  %add = add nsw i32 %div, %mul
  %2 = load i32, i32* %c.addr, align 4
  %mul1 = mul nsw i32 %2, 5
  %add2 = add nsw i32 %add, %mul1
  %3 = load i32, i32* %n.addr, align 4
  %mul3 = mul nsw i32 %3, 7
  %add4 = add nsw i32 %add2, %mul3
  %4 = load i32, i32* %n.addr, align 4
  %add5 = add nsw i32 %4, %add4
  store i32 %add5, i32* %n.addr, align 4
  %5 = load i32, i32* %a.addr, align 4
  %mul6 = mul nsw i32 %5, 11
  %6 = load i32, i32* %b.addr, align 4
  %div7 = sdiv i32 %6, 13
  %add8 = add nsw i32 %mul6, %div7
  %7 = load i32, i32* %c.addr, align 4
  %mul9 = mul nsw i32 %7, 17
  %add10 = add nsw i32 %add8, %mul9
  %8 = load i32, i32* %n.addr, align 4
  %mul11 = mul nsw i32 %8, 19
  %add12 = add nsw i32 %add10, %mul11
  %9 = load i32, i32* %b.addr, align 4
  %add13 = add nsw i32 %9, %add12
  store i32 %add13, i32* %b.addr, align 4
  %10 = load i32, i32* %a.addr, align 4
  %mul14 = mul nsw i32 %10, 23
  %11 = load i32, i32* %b.addr, align 4
  %mul15 = mul nsw i32 %11, 29
  %add16 = add nsw i32 %mul14, %mul15
  %12 = load i32, i32* %c.addr, align 4
  %div17 = sdiv i32 %12, 31
  %add18 = add nsw i32 %add16, %div17
  %13 = load i32, i32* %n.addr, align 4
  %mul19 = mul nsw i32 %13, 37
  %add20 = add nsw i32 %add18, %mul19
  %14 = load i32, i32* %c.addr, align 4
  %add21 = add nsw i32 %14, %add20
  store i32 %add21, i32* %c.addr, align 4
  %15 = load i32, i32* %a.addr, align 4
  %mul22 = mul nsw i32 %15, 41
  %16 = load i32, i32* %b.addr, align 4
  %mul23 = mul nsw i32 %16, 43
  %add24 = add nsw i32 %mul22, %mul23
  %17 = load i32, i32* %c.addr, align 4
  %mul25 = mul nsw i32 %17, 47
  %add26 = add nsw i32 %add24, %mul25
  %18 = load i32, i32* %n.addr, align 4
  %div27 = sdiv i32 %18, 53
  %add28 = add nsw i32 %add26, %div27
  %19 = load i32, i32* %a.addr, align 4
  %add29 = add nsw i32 %19, %add28
  store i32 %add29, i32* %a.addr, align 4
  %20 = load i32, i32* %a.addr, align 4
  ret i32 %20
}

; Function Attrs: noinline norecurse nounwind uwtable
define i32 @main() #1 {
entry:
  %a = alloca i32, align 4
  %b = alloca i32, align 4
  %c = alloca i32, align 4
  %i = alloca i32, align 4
  %call = call i32 @rand() #3
  %rem = srem i32 %call, 10
  store i32 %rem, i32* %a, align 4
  %call1 = call i32 @rand() #3
  %rem2 = srem i32 %call1, 10
  store i32 %rem2, i32* %b, align 4
  %call3 = call i32 @rand() #3
  %rem4 = srem i32 %call3, 10
  store i32 %rem4, i32* %c, align 4
  store i32 0, i32* %i, align 4
  %call5 = call i32 @rand() #3
  %rem6 = srem i32 %call5, 10
  store i32 %rem6, i32* %i, align 4
  %0 = load i32, i32* %a, align 4
  %1 = load i32, i32* %b, align 4
  %2 = load i32, i32* %c, align 4
  %3 = load i32, i32* %i, align 4
  %call7 = call i32 @_Z28test_resources_constraints_2iiii(i32 %0, i32 %1, i32 %2, i32 %3)
  ret i32 0
}

; Function Attrs: nounwind
declare i32 @rand() #2

attributes #0 = { noinline nounwind uwtable "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #1 = { noinline norecurse nounwind uwtable "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #2 = { nounwind "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #3 = { nounwind }

!llvm.module.flags = !{!0}
!llvm.ident = !{!1}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{!"clang version 6.0.1 (http://github.com/llvm-mirror/clang 2f27999df400d17b33cdd412fdd606a88208dfcc) (http://github.com/llvm-mirror/llvm 5136df4d089a086b70d452160ad5451861269498)"}
