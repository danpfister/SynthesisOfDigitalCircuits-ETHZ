; ModuleID = 'src/test_control_dependency_2.cpp'
source_filename = "src/test_control_dependency_2.cpp"
target datalayout = "e-m:e-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

; Function Attrs: noinline nounwind uwtable
define i32 @_Z25test_control_dependency_2iiii(i32 %a, i32 %b, i32 %c, i32 %n) #0 {
entry:
  %retval = alloca i32, align 4
  %a.addr = alloca i32, align 4
  %b.addr = alloca i32, align 4
  %c.addr = alloca i32, align 4
  %n.addr = alloca i32, align 4
  store i32 %a, i32* %a.addr, align 4
  store i32 %b, i32* %b.addr, align 4
  store i32 %c, i32* %c.addr, align 4
  store i32 %n, i32* %n.addr, align 4
  %0 = load i32, i32* %a.addr, align 4
  %1 = load i32, i32* %c.addr, align 4
  %div = sdiv i32 %0, %1
  %2 = load i32, i32* %b.addr, align 4
  %shl = shl i32 %div, %2
  %3 = load i32, i32* %n.addr, align 4
  %sub = sub nsw i32 %3, 6
  %cmp = icmp sge i32 %shl, %sub
  br i1 %cmp, label %if.then, label %if.else

if.then:                                          ; preds = %entry
  %4 = load i32, i32* %a.addr, align 4
  %5 = load i32, i32* %n.addr, align 4
  %shr = ashr i32 %4, %5
  %6 = load i32, i32* %b.addr, align 4
  %mul = mul nsw i32 %shr, %6
  store i32 %mul, i32* %a.addr, align 4
  %7 = load i32, i32* %a.addr, align 4
  %8 = load i32, i32* %b.addr, align 4
  %div1 = sdiv i32 %7, %8
  %9 = load i32, i32* %c.addr, align 4
  %shr2 = ashr i32 %div1, %9
  store i32 %shr2, i32* %c.addr, align 4
  br label %if.end11

if.else:                                          ; preds = %entry
  %10 = load i32, i32* %a.addr, align 4
  %11 = load i32, i32* %b.addr, align 4
  %add = add nsw i32 %10, %11
  %12 = load i32, i32* %n.addr, align 4
  %13 = load i32, i32* %c.addr, align 4
  %shr3 = ashr i32 %12, %13
  %mul4 = mul nsw i32 %add, %shr3
  %cmp5 = icmp sle i32 %mul4, 42
  br i1 %cmp5, label %if.then6, label %if.else7

if.then6:                                         ; preds = %if.else
  %14 = load i32, i32* %b.addr, align 4
  store i32 %14, i32* %retval, align 4
  br label %return

if.else7:                                         ; preds = %if.else
  %15 = load i32, i32* %b.addr, align 4
  %16 = load i32, i32* %a.addr, align 4
  %add8 = add nsw i32 %15, %16
  %17 = load i32, i32* %n.addr, align 4
  %mul9 = mul nsw i32 %add8, %17
  %18 = load i32, i32* %c.addr, align 4
  %shr10 = ashr i32 %mul9, %18
  store i32 %shr10, i32* %a.addr, align 4
  br label %if.end

if.end:                                           ; preds = %if.else7
  br label %if.end11

if.end11:                                         ; preds = %if.end, %if.then
  %19 = load i32, i32* %a.addr, align 4
  %20 = load i32, i32* %b.addr, align 4
  %add12 = add nsw i32 %19, %20
  %21 = load i32, i32* %n.addr, align 4
  %22 = load i32, i32* %c.addr, align 4
  %shr13 = ashr i32 %21, %22
  %mul14 = mul nsw i32 %add12, %shr13
  store i32 %mul14, i32* %c.addr, align 4
  %23 = load i32, i32* %c.addr, align 4
  store i32 %23, i32* %retval, align 4
  br label %return

return:                                           ; preds = %if.end11, %if.then6
  %24 = load i32, i32* %retval, align 4
  ret i32 %24
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
  %call7 = call i32 @_Z25test_control_dependency_2iiii(i32 %0, i32 %1, i32 %2, i32 %3)
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
